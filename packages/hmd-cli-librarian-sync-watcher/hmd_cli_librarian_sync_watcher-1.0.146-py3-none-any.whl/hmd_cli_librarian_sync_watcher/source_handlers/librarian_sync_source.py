from datetime import datetime, timezone
import logging
import os
from pathlib import Path
from typing import Dict, List, Union
from hmd_lang_librarian_sync.hmd_lang_librarian_sync_client import (
    File,
    HmdLangLibrarianSyncClient,
)
from hmd_lib_librarian_client.hmd_lib_librarian_client import HmdLibrarianClient
from .source import Source

logger = logging.getLogger(__name__)


class LibrarianSyncSource(Source):
    def __init__(
        self,
        config: Dict,
        librarian_sync_client: HmdLangLibrarianSyncClient,
        librarian_client: Union[HmdLibrarianClient, str],
        hmd_home: Path,
        hmd_repo_home: Path,
    ):
        config["content_globs"] = []  # No local content globs needed for librarian sync
        super().__init__(
            config, librarian_sync_client, librarian_client, hmd_home, hmd_repo_home
        )
        if not isinstance(self._librarian_client, HmdLibrarianClient):
            raise ValueError("LibrarianSyncSource requires HmdLibrarianClient instance")

        # Use librarian_client as source and target from config
        self.target_librarian = config.get("target")
        self.search_filters = config.get("search_filters", [])

    def sync(self):
        """
        Syncs content between librarians based on configured search filters.
        Queries the source librarian and creates File records for sync.
        """
        logger.info(
            f"{self.name}: Syncing content between librarians using search filters"
        )
        query = {"attribute": "source_name", "operator": "=", "value": self.name}
        downloaded_files: List[
            File
        ] = self._librarian_sync_client.search_file_hmd_lang_librarian_sync(query)
        last_updated = (
            sorted(map(lambda x: x.modified, downloaded_files))[-1]
            if downloaded_files
            else None
        )
        if last_updated:
            logger.info(
                f"{self.name}: Last sync was at {datetime.fromtimestamp(last_updated).astimezone(timezone.utc).isoformat()}"
            )
        else:
            logger.info(f"{self.name}: No previous sync found, performing full sync")

        for search_filter in self.search_filters:
            # Search source librarian using filter
            if last_updated:
                filter_ = {
                    "and": [
                        search_filter["filter"],
                        {
                            "attribute": "hmd_lang_librarian.content_item._updated",
                            "operator": ">",
                            "value": datetime.fromtimestamp(last_updated)
                            .astimezone(timezone.utc)
                            .isoformat(),
                        },
                    ]
                }
            else:
                filter_ = search_filter["filter"]
            results = self._librarian_client.search_librarian(filter_)

            for item in results:
                source_path = Path(self.path) / item["content_item_path"].replace(
                    ":/", "/"
                )

                if not source_path.exists():
                    os.makedirs(source_path.parent, exist_ok=True)
                self._librarian_client.get_file(
                    item["content_item_path"], source_path, force_overwrite=True
                )
                self.process_file(
                    source_path,
                    search_filter.get("content_item_type"),
                    search_filter.get("priority", 0),
                    search_filter.get("enable_checksum", self.enable_checksum),
                )

    async def watch(self):
        """
        Override watch to prevent watching local files since this source
        only handles librarian-to-librarian sync
        """
        logger.debug(f"{self.name}: watch not used for librarian sync source")
        pass

    def start(self):
        """
        Only perform initial sync since watching local files is not needed
        """
        logger.info(f"{self.name}: Starting librarian sync source")
        self.sync()
