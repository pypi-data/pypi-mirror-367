import asyncio
import copy
import getpass
import logging
import os
from pathlib import Path
import socket
from time import sleep
from cement import CaughtSignal

# import yaml
from hmd_cli_tools.hmd_cli_tools import get_env_var
from hmd_entity_storage import SqliteEngine
from hmd_graphql_client.hmd_db_engine_client import DbEngineClient
from hmd_lang_librarian_sync.hmd_lang_librarian_sync_client import (
    HmdLangLibrarianSyncClient,
    get_client_schema_root,
)
from hmd_lib_auth.hmd_lib_auth import (
    okta_service_account_token,
    okta_service_account_token_by_secret_name,
)
from hmd_lib_librarian_client.hmd_lib_librarian_client import HmdLibrarianClient
from hmd_schema_loader import DefaultLoader
import requests

from .config.validate_config import load_and_validate_config
from .log import build_dd_sender, get_dd_tags
from .source_handlers import make_source

logger = logging.getLogger(__name__)
send_datadog_event = build_dd_sender(logger)
OKTA_SECRET_NAME = "okta-agent-service"


def get_sleep_time(sleep_time: int = 1) -> int:
    return int(2**sleep_time) if sleep_time < 10 else 10


class LibrarianSyncManager:
    def __resolve_schema_location(self) -> Path:
        schema_location = Path(get_client_schema_root())
        if not schema_location.exists():
            schema_location = self.hmd_home / "language_packs"
        if not schema_location.exists():
            schema_location = (
                self.hmd_home / "client" / "vocabs" / "hmd-lang-librarian-sync"
            )
        if not schema_location.exists() and self.hmd_repo_home:
            schema_location = (
                self.hmd_repo_home / "hmd-lang-librarian-sync" / "src" / "schemas"
            )
        if not schema_location.exists() and self.schema_uri:
            schema_location = self.schema_uri
        if schema_location and schema_location.exists():
            return schema_location
        raise FileNotFoundError("Unable to resolve schema location")

    def __ensure_db(self) -> Path:
        db_location = self.hmd_home / "sqlite" / "data" / "librarian-sync.db"
        db_location.parent.mkdir(parents=True, exist_ok=True)
        return db_location

    def __build_client(
        self, schema_location: Path, db_location: Path
    ) -> HmdLangLibrarianSyncClient:
        loader = DefaultLoader(str(schema_location))
        engine = SqliteEngine(db_location)
        db_client = DbEngineClient(engine, loader)
        return HmdLangLibrarianSyncClient(db_client)

    def __init__(self, instance_config):
        self.hmd_home = Path(os.path.expandvars(get_env_var("HMD_HOME")))
        hmd_repo_home = get_env_var("HMD_REPO_HOME", False)
        if hmd_repo_home:
            self.hmd_repo_home = Path(os.path.expandvars(hmd_repo_home))
        else:
            self.hmd_repo_home = None
        self.schema_uri = None
        schema_uri = get_env_var("SCHEMA_URI", False)
        if schema_uri:
            self.schema_uri = Path(schema_uri)
        schema_location = self.__resolve_schema_location()
        db_location = self.__ensure_db()
        librarian_sync_client = self.__build_client(schema_location, db_location)
        self.librarian_sync_client = librarian_sync_client
        self.instance_config = instance_config

        if os.path.isfile(self.instance_config):
            self.abs_config_path = Path((Path.cwd() / self.instance_config).absolute())
            config = load_and_validate_config(self.abs_config_path, validate=False)
        else:
            config = load_and_validate_config(self.instance_config, validate=False)

        self.manifest_nid = os.environ.get("HMD_ENTITY_NID")
        for librarian_name, librarian in config["librarians"].items():
            if config["librarians"][librarian_name].get("url") == "default":
                url = os.environ.get(f"HMD_{librarian_name.upper()}_LIBRARIAN_URL")
                if url:
                    config["librarians"][librarian_name]["url"] = url
                else:
                    raise Exception(
                        f"Librarian {librarian_name} is not configured with an url endpoint."
                    )
            if config["librarians"][librarian_name].get("api_key"):
                if config["librarians"][librarian_name]["api_key"] == "default":
                    key = os.environ.get(f"HMD_{librarian_name.upper()}_LIBRARIAN_KEY")
                    config["librarians"][librarian_name]["api_key"] = (
                        key if key != "default" else None
                    )
            else:
                auth_token = None
                sleep_time = 0
                while auth_token is None:
                    try:
                        if self.manifest_nid:
                            auth_token = okta_service_account_token_by_secret_name(
                                OKTA_SECRET_NAME
                            )
                        else:
                            auth_token = okta_service_account_token(
                                os.environ["HMD_AGENT_CLIENT_ID"],
                                os.environ["HMD_AGENT_CLIENT_SECRET"],
                                okta_host_url=os.environ["HMD_SERVICES_ISSUER"],
                            )
                        config["librarians"][librarian_name]["auth_token"] = auth_token
                    except requests.exceptions.ConnectionError as e:
                        logger.error(
                            f"Connection error while retrieving auth token for {librarian_name}: {e}"
                        )
                        sleep_time = get_sleep_time(sleep_time)
                        sleep(sleep_time)  # Wait before retrying
                    except requests.exceptions.Timeout as e:
                        logger.error(
                            f"Timeout error while retrieving auth token for {librarian_name}: {e}"
                        )
                        sleep_time = get_sleep_time(sleep_time)
                        sleep(sleep_time)  # Wait before retrying
                    except Exception as e:
                        raise Exception(
                            f"Error retrieving auth token for {librarian_name}: {e}"
                        )

        self._config = config
        self.timestamp_reverse: bool = config.get("timestamp_sort", "asc") == "desc"

        self.archive_root = None
        if "archive_root" in self._config:
            self.archive_root = Path(os.path.expandvars(self._config["archive_root"]))

        def make_librarian_client(config):
            username = getpass.getuser()
            return HmdLibrarianClient(
                base_url=config.get("url"),
                api_key=config.get("api_key"),
                auth_token=config.get("auth_token"),
                extra_headers={
                    "X-NeuronSphere-User-Email": username,
                    "X-NeuronSphere-Host": os.environ.get(
                        "HMD_HOSTNAME", socket.gethostname()
                    ),
                },
            )

        librarian_clients = dict(
            map(
                lambda kv: (kv[0], make_librarian_client(kv[1])),
                self._config.get("librarians", {}).items(),
            )
        )

        def get_librarian_client(source_config):
            """Get the appropriate librarian client based on source type and configuration."""
            if source_config.get("type") == "librarian-sync":
                # For librarian-sync sources, use the target librarian
                return librarian_clients[source_config.get("target")]
            # For other sources, use the configured librarian
            return librarian_clients[source_config["librarian"]]

        all_sources = map(
            lambda kv: make_source(
                name=kv[0],
                source=kv[1],
                librarian_sync_client=librarian_sync_client,
                librarian_client=get_librarian_client(kv[1]),
                hmd_home=self.hmd_home,
                hmd_repo_home=self.hmd_repo_home,
                timestamp_reverse=self.timestamp_reverse,
            ),
            self._config["sources"].items(),
        )

        self.sources = list(filter(lambda x: x.is_enabled, all_sources))
        self.source_map = {s.name: s for s in self.sources}

    def get_queued_files(self):
        files = []
        for source in self.sources:
            files.extend(source.get_queued_files())
        # Sort based on modified time, default is older files first
        files = sorted(
            files,
            key=lambda f: f.modified,
            reverse=self.timestamp_reverse,
        )
        # Sort based on priority
        files = sorted(files, key=lambda f: f.upload_priority, reverse=True)
        return files

    def get_queued_file(self):
        files = self.get_queued_files()
        logger.info(len(files))
        while len(files) > 0:
            yield files[0]
            files = self.get_queued_files()
            logger.info(f"Found {len(files)} files...")
        logger.info("Return")
        return

    async def _sync(self, watch=True):
        logger.info("Validating config...")
        if os.path.isfile(self.instance_config):
            self.abs_config_path = Path((Path.cwd() / self.instance_config).absolute())
            is_valid, details = load_and_validate_config(
                self.abs_config_path, validate=True
            )
        else:
            is_valid, details = load_and_validate_config(
                self.instance_config, validate=True
            )
        if not is_valid:
            raise details
        logger.info("Config validated")
        sanitized_config = copy.copy(self._config)
        for lib_name, lib_config in sanitized_config["librarians"].items():
            if "auth_token" in lib_config:
                lib_config.pop("auth_token")
        logger.debug(f"Config: {sanitized_config}")
        send_datadog_event(
            event_type="success",
            data="Librarian sync manager configured successfully",
            tags=get_dd_tags(),
        )
        logger.info("BEGIN sync")
        while True:
            stop_requested = False
            is_complete = False
            attempt_max_reached = False
            if stop_requested:
                logger.info(f"{self.name}: Stop requested, skipping sync")
                break
            files = self.get_queued_files()
            is_complete = len(files) == 0
            gen = self.get_queued_file()
            for next_file in gen:
                if stop_requested:
                    logger.info(f"{self.name}: Stop requested, skipping sync")
                    break
                if next_file is None:
                    is_complete = True
                    break
                logger.info(f"Syncing queued file: {next_file.path}")
                source = self.source_map[next_file.source_name]
                source.attempts = 0
                try:
                    if not source.is_complete():
                        source.sync(next_file)
                except CaughtSignal as cs:
                    logger.error("Caught Signal", exc_info=cs)
                    stop_requested = True
                    break
                except BaseException as e:
                    logger.error("Sync failed", exc_info=e)
                    send_datadog_event(
                        event_type="error",
                        data=(
                            f"Librarian Sync Watcher failed during {source.name} sync"
                            if watch
                            else f"Librarian Sync Manager failed during {source.name} sync"
                        ),
                        ex=str(e),
                        tags=get_dd_tags(),
                    )
                    break
                source_is_complete = source.is_complete()
                is_complete = is_complete and source_is_complete
                if not source_is_complete:
                    attempt_max_reached = (
                        attempt_max_reached or source.attempt_max_reached()
                    )
                if source.type == "manifest":
                    query = {
                        "and": [
                            {
                                "attribute": "source_name",
                                "operator": "=",
                                "value": source.name,
                            }
                        ]
                    }
                    all_files = (
                        self.librarian_sync_client.search_file_hmd_lang_librarian_sync(
                            query
                        )
                    )
                    files_not_synced = [
                        file
                        for file in all_files
                        if file.librarians_synced[source.librarian] != file.modified
                        and file.schedule_upload != 1
                    ]
                    if len(files_not_synced) == 0 and source.type == "manifest":
                        for file in all_files:
                            if Path(file.path).exists():
                                source.handle_file_delete(file)
            if stop_requested:
                break
            if watch:
                await asyncio.sleep(5)

            elif is_complete:
                break
            elif attempt_max_reached:
                send_datadog_event(
                    event_type="error",
                    data=(
                        "Librarian Sync Watcher failure"
                        if watch
                        else "Librarian Sync Manager failure"
                    ),
                    ex="Max attempts reached",
                    tags=get_dd_tags(),
                )
        logger.info("END sync")

    def sync(self):
        try:
            asyncio.run(self._sync(False))
        except BaseException as e:
            logger.error("Manager Sync failed", exc_info=e)
            send_datadog_event(
                event_type="error",
                data="Librarian sync manager failed during sync",
                ex=str(e),
                tags=get_dd_tags(),
            )
            raise e

    def start(self):
        try:
            logger.info("Starting watcher")
            send_datadog_event(
                event_type="info",
                data="Librarian sync watcher started",
                tags=get_dd_tags(),
            )
            asyncio.run(self._sync())
        except BaseException as e:
            logger.error("Watcher failed", exc_info=e)
            send_datadog_event(
                event_type="error",
                data="Librarian sync watcher failed to sync",
                ex=str(e),
                tags=get_dd_tags(),
            )
            raise e

    def stop(self):
        logger.info("Stopping Manager")
        for source in self.sources:
            source.stop()
        logger.info("all tasks stopped")
        send_datadog_event(
            event_type="info", data="Librarian sync manager stopped", tags=get_dd_tags()
        )
