import json
import logging
import os
from pathlib import Path
from typing import Dict, List

from hmd_lang_librarian_sync.file import File
from hmd_lang_librarian_sync.hmd_lang_librarian_sync_client import (
    HmdLangLibrarianSyncClient,
)
from hmd_lib_librarian_client.hmd_lib_librarian_client import (
    HmdLibrarianClient,
    NoSuchContentItemException,
)

from .source import Source, check_token_exp

logger = logging.getLogger(__name__)


class ManifestSource(Source):
    def __init__(
        self,
        config: Dict,
        librarian_sync_client: HmdLangLibrarianSyncClient,
        librarian_client: HmdLibrarianClient,
        hmd_home: Path,
        hmd_repo_home: Path,
        timestamp_reverse: bool,
    ):
        super().__init__(
            config,
            librarian_sync_client,
            librarian_client,
            hmd_home,
            hmd_repo_home,
            timestamp_reverse,
        )
        self.manifest_content_item_type = config.get(
            "manifest_content_item_type", "hmd-manifest"
        )
        self.manifest_file_name = config.get(
            "manifest_file_name",
            f"hmd-librarian-{self.manifest_content_item_type.replace('_', '-')}.json",
        )
        self.librarian = librarian_client.base_client.base_url

        if self.is_enabled:
            if self.is_pull:
                self.manifest_content_path = os.environ.get("HMD_ENTITY_CONTENT_PATH")
                self.manifest_nid = os.environ.get("HMD_ENTITY_NID")
                out_path = config.get("out_path", config.get("path"))
                self.out_path: Path = Path(os.path.expandvars(out_path)).expanduser()
                self.manifest_path = self.out_path / self.manifest_file_name
                if not self.manifest_path.exists():
                    if self._librarian_client.base_client.auth_token:
                        auth_token = check_token_exp(
                            self._librarian_client.base_client.auth_token
                        )
                        if auth_token:
                            self._librarian_client = HmdLibrarianClient(
                                base_url=self.librarian, auth_token=auth_token
                            )
                            logger.info(f"Auth token refreshed for {self.librarian}")
                    if self.manifest_nid:
                        try:
                            logger.info("Getting file from manifest nid..")
                            self._librarian_client.get_file_by_nid(
                                self.manifest_nid, self.manifest_path
                            )
                        except NoSuchContentItemException as e:
                            logger.error(e)
                    elif self.manifest_content_path:
                        try:
                            logger.info("Getting file from manifest content path..")
                            self._librarian_client.get_file(
                                self.manifest_content_path, self.manifest_path
                            )
                        except NoSuchContentItemException as e:
                            logger.error(e)
                    else:
                        raise Exception(
                            f"Manifest not found under nid: {self.manifest_nid} "
                            f"or content path: {self.manifest_content_path}."
                        )

                with open(self.manifest_path) as manifest:
                    self.manifest_data = json.loads(manifest.read())

    def get_queued_files(self):
        logger.info(f"{self.name}: Getting queued files")
        query = {
            "and": [
                {"attribute": "source_name", "operator": "=", "value": self.name},
                {
                    "attribute": "content_item_type",
                    "operator": "=",
                    "value": self.manifest_content_item_type,
                },
                {"attribute": "schedule_upload", "operator": "<", "value": 1},
            ]
        }
        manifests = self._librarian_sync_client.search_file_hmd_lang_librarian_sync(
            query
        )
        files = []
        for manifest in manifests:
            manifest = self.update_librarians_synced(manifest)

            if manifest.librarians_synced[self.librarian] == manifest.modified:
                logger.info(f"Manifest already synced: {manifest.serialize()}")
                continue
            content_file_rels = (
                self._librarian_sync_client.get_from_file_file_hmd_lang_librarian_sync(
                    manifest
                )
            )
            content_files = map(
                lambda x: (
                    self._librarian_sync_client.get_file_hmd_lang_librarian_sync(
                        x.ref_to
                    )
                    if type(x.ref_to) == str
                    else x.ref_to
                ),
                content_file_rels,
            )
            content_files = map(self.update_librarians_synced, content_files)
            queued_content_files = list(
                filter(
                    lambda x: x.modified != x.librarians_synced[self.librarian]
                    and x.schedule_upload != 1,
                    content_files,
                )
            )
            if len(queued_content_files) > 0:
                files.extend(queued_content_files)
            else:
                files.append(manifest)
        # Sort based on modified time, default is older files first
        files = sorted(
            files,
            key=lambda f: f.modified,
            reverse=self.timestamp_reverse,
        )
        # Sort based on priority
        files = sorted(files, key=lambda f: f.upload_priority, reverse=True)
        return files

    def _get_unpulled_files(self):
        # TODO: update to pull files from relationships instead of manifest data
        files = self.manifest_data.get("files", [])
        return list(
            filter(lambda x: not (self.out_path / x.get("file_path")).exists(), files)
        )

    def pull_files(self):
        unpulled_files = self._get_unpulled_files()
        for file in unpulled_files:
            item_path = file.get("file_path").split("\\")
            if len(item_path) > 1:
                logger.info(f"reformatting Windows path...")
                file_path: Path = self.out_path / "/".join(item_path)
            else:
                file_path: Path = self.out_path / file.get("file_path")
            content_path = file.get("content_path")

            logger.info(f"Pulling {content_path} to {file_path}")
            file_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                self._librarian_client.get_file(content_path, file_path)
            except Exception as e:
                if self._librarian_client.base_client.auth_token:
                    auth_token = check_token_exp(
                        self._librarian_client.base_client.auth_token
                    )
                    if auth_token:
                        self._librarian_client = HmdLibrarianClient(
                            base_url=self.librarian, auth_token=auth_token
                        )
                        logger.info(f"Auth token refreshed for {self.librarian}")
                    else:
                        logger.error(f"{self.name}: error putting file", exc_info=e)
                else:
                    logger.error(f"{self.name}: error putting file", exc_info=e)

    def is_complete(self):
        if self.is_push:
            return 0 == len(self.get_queued_files())
        else:
            return 0 == len(self._get_unpulled_files())
