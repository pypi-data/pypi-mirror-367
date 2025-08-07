from pathlib import Path
from typing import Dict

from hmd_lang_librarian_sync.hmd_lang_librarian_sync_client import (
    HmdLangLibrarianSyncClient,
)
from hmd_lib_librarian_client.hmd_lib_librarian_client import HmdLibrarianClient

from .librarian_sync_source import LibrarianSyncSource
from .manifest_source import ManifestSource
from .source import Source


def make_source(
    name: str,
    source: Dict,
    librarian_sync_client: HmdLangLibrarianSyncClient,
    librarian_client: HmdLibrarianClient,
    hmd_home: Path,
    hmd_repo_home: Path,
    timestamp_reverse: bool = False,
) -> Source:
    """Create a source handler based on source configuration."""
    source = dict(source)
    source["name"] = name
    source_type = source.get("type", "default")

    if source_type == "manifest":
        return ManifestSource(
            source,
            librarian_sync_client,
            librarian_client,
            hmd_home,
            hmd_repo_home,
            timestamp_reverse,
        )
    elif source_type == "librarian-sync":
        return LibrarianSyncSource(
            source,
            librarian_sync_client,
            librarian_client,
            hmd_home,
            hmd_repo_home,
            timestamp_reverse,
        )
    else:
        return Source(
            source,
            librarian_sync_client,
            librarian_client,
            hmd_home,
            hmd_repo_home,
            timestamp_reverse,
        )
