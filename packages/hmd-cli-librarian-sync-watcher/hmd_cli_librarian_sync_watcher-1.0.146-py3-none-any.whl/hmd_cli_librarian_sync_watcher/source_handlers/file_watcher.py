import fnmatch
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional, Set

from watchgod import AllWatcher, Change
from watchgod.main import awatch

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from watchgod.watcher import FileChange


class AbsoluteWatcher(AllWatcher):
    def __init__(self, file_path: str):
        self.file_path = file_path
        super().__init__(file_path)

    def should_watch_file(self, entry: "os.DirEntry") -> bool:
        return self.file_path == entry.path


class GlobWatcher(AllWatcher):
    def __init__(self, root_path: str, file_globs: Optional[str] = None):
        self.file_globs = file_globs
        self.root_path_not_found_time = None
        super().__init__(root_path)

    def should_watch_file(self, entry: "os.DirEntry") -> bool:
        if self.file_globs is not None:
            val = next(
                filter(
                    lambda file_glob: fnmatch.fnmatch(entry.path, file_glob),
                    self.file_globs,
                ),
                None,
            )
            return val
        else:
            return super().should_watch_file(entry)

    def check(self) -> Set["FileChange"]:
        changes: Set["FileChange"] = set()
        new_files: Dict[str, float] = {}
        try:
            if Path(self.root_path).is_dir():
                if self.root_path_not_found_time is not None:
                    logger.info(
                        f"Root Path access restored: {self.root_path} after {datetime.now() - self.root_path_not_found_time}"
                    )
                    self.root_path_not_found_time = None
                self._walk(self.root_path, changes, new_files)
            else:
                if self.root_path_not_found_time is None:
                    self.root_path_not_found_time = datetime.now()
                    logger.info(
                        f"Root Path access lost: {self.root_path} at {self.root_path_not_found_time}"
                    )
        except OSError as e:
            # happens when a directory has been deleted between checks
            logger.info("errors walking file system: %s %s", e.__class__.__name__, e)

        # look for deleted
        deleted = self.files.keys() - new_files.keys()
        if deleted:
            changes |= {(Change.deleted, entry) for entry in deleted}

        self.files = new_files
        return changes
