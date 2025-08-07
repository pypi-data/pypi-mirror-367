import logging
from datetime import datetime
from operator import itemgetter
from pathlib import Path
from typing import Dict, List
from hmd_lang_librarian_sync.file import File
from hmd_lang_librarian_sync.file_file import FileFile
from hmd_lang_librarian_sync.hmd_lang_librarian_sync_client import (
    HmdLangLibrarianSyncClient,
)

from .source import Source

logger = logging.getLogger(__name__)


class ManifestSource(Source):
    def __init__(
        self,
        config: Dict,
        librarian_sync_client: HmdLangLibrarianSyncClient,
        librarian_client,
        hmd_home: Path,
        hmd_repo_home: Path,
    ):
        super().__init__(
            config, librarian_sync_client, librarian_client, hmd_home, hmd_repo_home
        )
        self.manifest_file_name = config.get(
            "manifest_file_name", "hmd-librarian-manifest.json"
        )
        if self.is_push:
            self.manifest_content_item_type = config.get(
                "manifest_content_item_type", "hmd-manifest"
            )
            self.manifest_content_globs = [
                {
                    "globs": a["globs"],
                    "content_item_type": a["content_item_type"],
                    "priority": a.get("priority", 0),
                }
                for a in config["manifest_content_globs"]
            ]
            self.generate_manifest = config.get("generate_manifest", True)
            self.push_trigger_file = config.get("push_trigger_file", False)

    def process_file(
        self,
        file_path: Path,
        trigger_content_item_type: str,
        priority: int = 0,
        enable_checksum: bool = False,
    ):
        logger.info(
            f"{self.name}: Process manifest file: {str(file_path)} - {trigger_content_item_type}"
        )
        if Path(file_path).is_file():
            # metadata = self.get_metadata(file_path)
            manifest_root = Path(file_path).parent
        else:
            # metadata = {}
            manifest_root = Path(file_path)

        files_dict = dict()
        for manifest_content_glob in self.manifest_content_globs:
            content_globs, content_item_type, priority = itemgetter(
                "globs", "content_item_type", "priority"
            )(manifest_content_glob)
            qualified_globs = self.resolve_globs(content_globs, manifest_root)
            for res in self.gather_globs_results(qualified_globs):
                if Path(res).is_file():
                    files_dict[res] = (content_item_type, priority, enable_checksum)

        if Path(file_path).is_file():
            metadata = self.get_metadata(file_path)
        elif len(files_dict) > 0:
            metadata = self.get_metadata(list(files_dict.keys())[0])
        else:
            logger.info(f"No relevant files under {file_path}. Skipping..")
            return None

        if self.generate_manifest:
            logger.info(f"{self.name}: Generating manifest for {file_path}")
            import json

            def get_content_item(item_path: Path):
                metadata = self.get_metadata(item_path)
                return {
                    "content_item_type": files_dict[item_path][0],
                    "content_path": self.generate_content_path(
                        item_path, metadata, manifest_root
                    ),
                    "item_path": item_path,
                    "priority": files_dict[item_path][1],
                }

            self.manifest_file_name = self.manifest_file_name.format(**metadata)
            manifest_path = manifest_root / self.manifest_file_name

            content_items = list(
                filter(
                    lambda x: Path(x["item_path"]) != manifest_path,
                    map(get_content_item, sorted(files_dict)),
                )
            )

            manifest_files = list(
                map(
                    lambda x: {
                        "file_path": str(
                            Path(x["item_path"]).relative_to(manifest_root)
                        ).replace("\\", "/"),
                        "content_path": x["content_path"],
                        "modified_time": str(
                            datetime.fromtimestamp(Path(x["item_path"]).stat().st_mtime)
                        ),
                    },
                    content_items,
                )
            )

            manifest_content_path = self.generate_content_path(
                manifest_path, metadata, manifest_root
            )

            manifest_data = {"files": manifest_files}
            manifest_data_str = json.dumps(manifest_data, indent=2)
            manifest_file_content_str = ""

            if manifest_path.exists():
                with open(manifest_path, "r") as infile:
                    manifest_file_content_str = infile.read()

            if (
                manifest_file_content_str
                and manifest_file_content_str != manifest_data_str
            ):
                old_manifest_data = json.loads(manifest_file_content_str)
                new_files = old_manifest_data["files"]
                for file in manifest_data["files"]:
                    if file not in new_files:
                        new_files.append(file)
                manifest_data["files"] = new_files
                with open(manifest_path, "w") as outfile:
                    json.dump(manifest_data, outfile, indent=2)
            elif not manifest_file_content_str:
                with open(manifest_path, "w") as outfile:
                    json.dump(manifest_data, outfile, indent=2)

            files: List[File] = []
            for content_item in content_items:
                content_item_type, content_path, item_path, priority = itemgetter(
                    "content_item_type", "content_path", "item_path", "priority"
                )(content_item)
                if Path(item_path).is_file():
                    file = self.upsert_file(
                        Path(item_path),
                        content_item_type,
                        content_path,
                        priority,
                        enable_checksum,
                    )
                    files.append(file)

            manifest_file = self.upsert_file(
                manifest_path,
                self.manifest_content_item_type,
                manifest_content_path,
                priority,
                enable_checksum,
            )
            relationships = (
                self._librarian_sync_client.get_from_file_file_hmd_lang_librarian_sync(
                    manifest_file
                )
            )
            for file in files:
                logger.info(
                    f"{self.name}: Upserting relationship: {manifest_file.content_path} -> {file.content_path} --- {file.identifier}"
                )

                relationship = next(
                    (x for x in relationships if x.ref_to == file.identifier), None
                )
                if relationship == None:
                    relationship = FileFile(
                        ref_from=manifest_file.identifier,
                        ref_to=file.identifier,
                        source_name=self.name,
                    )
                    relationship = self._librarian_sync_client.upsert_file_file_hmd_lang_librarian_sync(
                        relationship
                    )
                    logger.info(
                        f"{self.name}: Relationship created: {relationship.identifier}"
                    )
                else:
                    logger.info(f"{self.name}: Relationship already exists")
        elif self.push_trigger_file:
            if file_path.is_file():
                meta_content_path = self.generate_content_path(file_path, metadata)
                self.upsert_file(
                    Path(file_path), trigger_content_item_type, meta_content_path
                )
            else:
                logger.info("Trigger is a directory and will not be pushed.")
