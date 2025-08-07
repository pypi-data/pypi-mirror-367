import logging
import os
from pathlib import Path
from typing import Dict

from hmd_lang_librarian_sync.file import File
from hmd_lang_librarian_sync.hmd_lang_librarian_sync_client import (
    HmdLangLibrarianSyncClient,
)
from hmd_lib_librarian_client.hmd_lib_librarian_client import (
    HmdLibrarianClient,
)

from .source import Source, check_token_exp

logger = logging.getLogger(__name__)


class LibrarianSyncSource(Source):
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
        self.source_librarian_name = config.get("source")
