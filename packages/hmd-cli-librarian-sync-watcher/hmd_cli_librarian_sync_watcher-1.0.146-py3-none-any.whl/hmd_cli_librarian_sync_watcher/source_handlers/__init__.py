import logging
from pathlib import Path
from typing import Dict

from hmd_lang_librarian_sync.hmd_lang_librarian_sync_client import (
    HmdLangLibrarianSyncClient,
)
from hmd_lib_librarian_client.hmd_lib_librarian_client import HmdLibrarianClient
from .manifest_source import ManifestSource
from .librarian_sync_source import LibrarianSyncSource
from .source import Source

logger = logging.getLogger(__name__)


def make_source(
    name: str,
    source: Dict,
    librarian_sync_client: HmdLangLibrarianSyncClient,
    librarian_client: HmdLibrarianClient,
    hmd_home: Path,
    hmd_repo_home: Path,
) -> Source:
    source["name"] = name
    source_type = source.get("type", "default")
    logger.info(f"{source['name']}: creating source of type {source_type}")
    if source_type == "manifest":
        return ManifestSource(
            source, librarian_sync_client, librarian_client, hmd_home, hmd_repo_home
        )
    elif source_type == "librarian-sync":
        return LibrarianSyncSource(
            source, librarian_sync_client, librarian_client, hmd_home, hmd_repo_home
        )
    return Source(
        source, librarian_sync_client, librarian_client, hmd_home, hmd_repo_home
    )
