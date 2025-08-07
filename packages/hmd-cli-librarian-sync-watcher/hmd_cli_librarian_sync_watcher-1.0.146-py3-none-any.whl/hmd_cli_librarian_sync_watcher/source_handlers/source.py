import datetime
import errno
import glob
import hashlib
import logging
import os
from itertools import chain
from operator import itemgetter
from pathlib import Path, PurePath
from typing import Dict, List, Set, Union
from hmd_lang_librarian_sync.hmd_lang_librarian_sync_client import (
    File,
    FileUpload,
    FileToUpload,
    HmdLangLibrarianSyncClient,
)
from hmd_lib_librarian_client.hmd_lib_librarian_client import HmdLibrarianClient
from watchgod import Change
from watchgod.main import awatch
from .file_watcher import GlobWatcher
from wcmatch import fnmatch

logger = logging.getLogger(__name__)


class MetaPluginNotFoundError(FileExistsError):
    def __init__(self, module_path):
        super().__init__(
            errno.ENOENT, "Metadata plugin file not found", str(module_path)
        )


class Source:
    def __init__(
        self,
        config: Dict,
        librarian_sync_client: HmdLangLibrarianSyncClient,
        librarian_client: Union[HmdLibrarianClient, str],
        hmd_home: Path,
        hmd_repo_home: Path,
    ):
        self._librarian_sync_client = librarian_sync_client
        self._librarian_client = librarian_client
        self._hmd_home = hmd_home
        self._hmd_repo_home = hmd_repo_home
        self.name: str = config["name"]
        self.path: Path = Path(os.path.expandvars(config["path"])).expanduser()
        if isinstance(self._librarian_client, HmdLibrarianClient):
            self.librarian = self._librarian_client.base_client.base_url
        else:
            self.librarian = librarian_client
        self.is_enabled: bool = config.get("enabled", True)
        direction: str = config.get("direction", "push")
        self.is_push = direction == "push"
        self.is_pull = direction == "pull"
        self.manifest_nid = os.environ.get("HMD_ENTITY_NID")
        self.enable_checksum = config.get("enable_checksum", False)
        if self.is_push:
            self.content_globs = [
                {
                    "globs": self.resolve_globs(a["globs"]),
                    "content_item_type": a["content_item_type"],
                    "priority": a.get("priority", 0),
                }
                for a in config["content_globs"]
            ]
            self.content_globs.sort(key=lambda g: g["priority"], reverse=True)

            self.upload_path: str = config["upload_path"]
            self.encode_special_characters = config.get(
                "encode_special_characters", False
            )
            self.encode_trailing_path_segments = config.get(
                "encode_trailing_path_segments", False
            )
            if "meta_script" in config:
                self.meta_script = config["meta_script"]
                if os.environ.get("META_SCRIPT"):
                    logger.info(os.environ["META_SCRIPT"])
                    plugin = os.environ["META_SCRIPT"]
                    with open(
                        self._hmd_home
                        / ".config"
                        / "plugins"
                        / f"{self.meta_script}.py",
                        "w",
                    ) as plugin_file:
                        plugin_file.write(plugin)
                self.meta_plugin = self.load_plugin(
                    self.meta_script, self._hmd_home / ".config" / "plugins"
                )
            else:
                self.meta_plugin = self.load_plugin(
                    "default_meta_plugin", Path(__file__).parent.resolve()
                )
        else:
            self.is_enabled = False

    def load_plugin(self, module_name, context_path: Path):
        module_path = context_path / f"{module_name}.py"
        logger.info(f"{self.name}: Loading plugin '{module_name}' from '{module_path}'")
        if module_path.exists():
            import importlib.util

            spec = importlib.util.spec_from_file_location(module_name, str(module_path))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        else:
            raise MetaPluginNotFoundError(module_path)

    def get_metadata(self, file_path: Path) -> Dict:
        return self.meta_plugin.get_metadata(str(file_path))

    def resolve_globs(self, globs: List[str], root: Path = None) -> List[str]:
        if root is None:
            root = self.path
        return list(map(lambda pattern: str(root / pattern), globs))

    def get_content_item_type(self, path: Path):
        content_item_type = None
        p = PurePath(path)
        priority = 0
        enable_checksum = self.enable_checksum
        for content_glob in self.content_globs:
            for glob in content_glob["globs"]:
                if fnmatch.fnmatch(str(p), glob):
                    content_item_type = content_glob["content_item_type"]
                    priority = content_glob["priority"]
                    enable_checksum = content_glob.get(
                        "enable_checksum", self.enable_checksum
                    )
                    break
        return content_item_type, priority, enable_checksum

    def watch_handler(self, changes: Set[Change]):
        logger.info(f"{self.name}: handling {len(changes)} change(s)")
        for change_type, change_path in changes:
            if change_type == 3:
                logger.info(f"{self.name}: Ignoring delete event for {change_path}")
            else:
                try:
                    path = Path(change_path)
                    cit, priority, enable_checksum = self.get_content_item_type(path)
                    self.process_file(
                        path, cit, priority, enable_checksum=enable_checksum
                    )
                except Exception as ex:
                    logger.error(
                        f"{self.name}: Exception while processing file: {change_path}",
                        exc_info=ex,
                    )

    async def watch(self):
        logger.info(f"{self.name}: Registering Watcher - {self.path}")

        globs = list(chain.from_iterable(map(lambda x: x["globs"], self.content_globs)))

        awatch_kwargs = {
            "watcher_cls": GlobWatcher,
            "watcher_kwargs": dict(file_globs=globs),
        }
        watcher = awatch(self.path, **awatch_kwargs)
        async for changes in watcher:
            self.watch_handler(changes)

    def gather_globs_results(self, globs):
        results = []
        for g in globs:
            for file in glob.iglob(str(g), recursive=True):
                file_path = Path(file)
                if os.name == "nt":
                    path_parts = str(file_path).split("\\")
                    results.append("/".join(path_parts))
                else:
                    results.append(file_path)
        return results

    def sync(self):
        logger.info(f"{self.name}: Syncing existing files - {self.path}")
        files_dict = dict()
        for content_glob in self.content_globs:
            content_globs, content_item_type, priority = itemgetter(
                "globs", "content_item_type", "priority"
            )(content_glob)
            for res in self.gather_globs_results(content_globs):
                logger.debug(f"Found file: {res} - {content_item_type} - {priority}")
                files_dict[res] = (
                    content_item_type,
                    priority,
                    content_glob.get("enable_checksum", self.enable_checksum),
                )
        for path, value in files_dict.items():
            self.process_file(
                Path(path), value[0], priority=value[1], enable_checksum=value[2]
            )

    def start(self):
        self.sync()
        logger.info(f"{self.name}: Starting watcher - {self.path}")
        return self.watch()

    def process_file(
        self,
        file_path: Path,
        content_item_type: str,
        priority: int = 0,
        enable_checksum: bool = False,
    ):
        logger.info(f"{self.name}: Process default file: {str(file_path)}")
        metadata = self.get_metadata(file_path)
        content_path = self.generate_content_path(file_path, metadata)
        if content_path:
            self.upsert_file(
                file_path, content_item_type, content_path, priority, enable_checksum
            )

    def get_file_by_content_path(self, content_path):
        query = {"attribute": "content_path", "operator": "=", "value": content_path}
        results = self._librarian_sync_client.search_file_hmd_lang_librarian_sync(query)
        if len(results) == 1:
            return results[0]
        return None

    def get_file_by_source_path(self, source_path: Path):
        query = {"attribute": "path", "operator": "=", "value": str(source_path)}
        results = self._librarian_sync_client.search_file_hmd_lang_librarian_sync(query)
        if len(results) == 1:
            return results[0]
        return None

    def generate_content_path(
        self, path: Path, metadata: Dict = {}, root_path: Path = None
    ):
        if root_path is None:
            root_path = self.path
        segment_seperator = "/"
        upload_path_segments = [
            self.process_upload_path_segment(path, segment)
            for segment in self.upload_path.split(segment_seperator)
        ]
        meta_values = {f"meta_{str(key)}": val for key, val in metadata.items()}
        relative_path = str(Path(path).relative_to(root_path))

        # TODO remove this
        # special_characters = []
        # if self.encode_special_characters:
        #     # TODO what other special characters do we need to account for?
        #     special_characters.extend(["!"])
        # if self.encode_trailing_path_segments:
        #     special_characters.append(os.sep)
        #     if os.altsep:
        #         special_characters.append(os.altsep)

        # for special_character in special_characters:
        #     replacement = f"__{ord(special_character)}__"
        #     relative_path = relative_path.replace(special_character, replacement)

        # Normalize path seperators
        relative_path = relative_path.replace(os.sep, segment_seperator)
        if os.altsep:
            relative_path = relative_path.replace(os.altsep, segment_seperator)
        if "{manifest_base_path}" in upload_path_segments:
            if self.manifest_nid:
                try:
                    content_path = self._librarian_client._get_by_nid(
                        {"nids": [self.manifest_nid]}
                    )[0]["content_item"]["content_item_path"]
                    file_name = os.path.basename(content_path)
                    manifest_base_path = content_path.split(":/")[1].replace(
                        "/" + file_name, ""
                    )
                    if len(manifest_base_path.split("/")) > 3:
                        manifest_base_path = manifest_base_path.replace(
                            "/" + os.path.basename(manifest_base_path), ""
                        )
                except BaseException as e:
                    logger.info(f"Error getting manifest_base_path: {e}")
            else:
                raise Exception(
                    "Manifest nid not available to generate base upload path from."
                )
            content_path_parameters = {
                "relative_path": relative_path,
                "short_file_name": Path(path).name,
                "source_path": Path(path).parts,
                "manifest_base_path": manifest_base_path,
                **meta_values,
            }
        else:
            content_path_parameters = {
                "relative_path": relative_path,
                "short_file_name": Path(path).name,
                "source_path": Path(path).parts,
                **meta_values,
            }
        content_path = segment_seperator.join(upload_path_segments).format(
            **content_path_parameters
        )
        content_path_prefix = content_path[: content_path.index(":")]
        content_path_suffix = content_path[content_path.index(":") + 1 :]
        sanitized_content_path_suffix = content_path_suffix

        spec_chars = "|#<>~[]`%{}^\\?, +:;=@$&"
        for spec_char in spec_chars:
            sanitized_content_path_suffix = sanitized_content_path_suffix.replace(
                spec_char, f"__{ord(spec_char)}__"
            )
        final_content_path = f"{content_path_prefix}:{sanitized_content_path_suffix}"

        logger.debug(
            f"{self.name}: computed contentpath for {path}: {final_content_path}"
        )
        return final_content_path

    def cancel_pending_uploads(self, file: File):
        """
        Cancels any existing FileUpload entities with 'pending' or 'uploading' statuses
        for the given File entity.
        """
        existing_file_upload_rels = (
            self._librarian_sync_client.get_from_file_to_upload_hmd_lang_librarian_sync(
                file
            )
        )

        existing_file_uploads = self._librarian_sync_client._base_client.get_entities(
            "hmd_lang_librarian_sync.file_upload",
            [rel.ref_to for rel in existing_file_upload_rels],
        )

        for existing_file_upload in existing_file_uploads:
            if existing_file_upload and existing_file_upload.upload_status in [
                "pending",
                "uploading",
            ]:
                logger.info(
                    f"{self.name}: Canceling existing FileUpload for file {file.path}"
                )
                existing_file_upload.upload_status = "canceled"
                self._librarian_sync_client.upsert_file_upload_hmd_lang_librarian_sync(
                    existing_file_upload
                )

    def create_pending_file_upload(self, file: File, source_path: Path):
        """
        Creates a new pending FileUpload and relates it to the given File entity.
        """
        logger.info(
            f"{self.name}: Creating new FileUpload for updated file {str(source_path)}"
        )
        file_checksum = self._librarian_client.calculate_checksum(source_path)
        file_size = source_path.stat().st_size
        new_file_upload = FileUpload(
            upload_status="pending",
            file_checksum=file_checksum,
            file_checksum_algorithm="CRC64NVME",
            file_size=file_size,
            content_item_path=file.content_path,
        )
        new_file_upload = (
            self._librarian_sync_client.upsert_file_upload_hmd_lang_librarian_sync(
                new_file_upload
            )
        )
        self._librarian_sync_client.upsert_file_to_upload_hmd_lang_librarian_sync(
            FileToUpload(ref_from=file.identifier, ref_to=new_file_upload.identifier)
        )

    def upsert_file(
        self,
        source_path: Path,
        content_item_type: str,
        content_path: str,
        priority: int = 0,
        enable_checksum: bool = False,
    ):
        logger.info(f"{self.name}: upserting file {str(source_path)}")

        modified_time = int(source_path.stat().st_mtime)

        file = self.get_file_by_source_path(source_path)
        if enable_checksum:
            file_checksum = self._librarian_client.calculate_checksum(source_path)
        else:
            file_checksum = None
        if file:
            if self.librarian not in file.librarians_synced.keys():
                file.librarians_synced[self.librarian] = ""
                file.schedule_upload = 0
                file = self._librarian_sync_client.upsert_file_hmd_lang_librarian_sync(
                    file
                )
            if (
                file.content_path != content_path
                or file.content_item_type != content_item_type
                or file.modified != modified_time
                or file.upload_priority != priority
            ):
                logger.info(f"{self.name}: updating file {str(source_path)}")
                file.content_item_type = content_item_type
                file.content_path = content_path
                file.modified = modified_time
                file.upload_priority = priority
                file.schedule_upload = 0
                if enable_checksum:
                    file.checksum = {"value": file_checksum, "algorithm": "CRC64NVME"}
                # Upsert FileUpload entity if the file has changed
                self.cancel_pending_uploads(file)

                self.create_pending_file_upload(file, source_path)

                return self._librarian_sync_client.upsert_file_hmd_lang_librarian_sync(
                    file
                )
            else:
                if file.librarians_synced[self.librarian] != file.modified:
                    logger.info(
                        f"{self.name}: file {str(source_path)} has been modified"
                    )
                    file.schedule_upload = 0
                    # Upsert FileUpload entity if the file has changed
                    logger.info(
                        f"{self.name}: Creating new FileUpload for updated file {str(source_path)}"
                    )
                    self.cancel_pending_uploads(file)
                    self.create_pending_file_upload(file, source_path)
                else:
                    logger.info(
                        f"{self.name}: file already up-to-date {str(source_path)}"
                    )
                    file.schedule_upload = 1
                file = self._librarian_sync_client.upsert_file_hmd_lang_librarian_sync(
                    file
                )
                return file
        else:
            logger.info(f"{self.name}: inserting file {str(source_path)}")
            file = File(
                path=str(source_path),
                content_path=content_path,
                content_item_type=content_item_type,
                modified=modified_time,
                librarians_synced={self.librarian: ""},
                source_name=self.name,
                upload_priority=priority,
                schedule_upload=0,
            )
            if enable_checksum:
                file.checksum = {"value": file_checksum, "algorithm": "CRC64NVME"}

            file = self._librarian_sync_client.upsert_file_hmd_lang_librarian_sync(file)
            self.create_pending_file_upload(file, source_path)
            return file

    def hash_file(self, path: Path):
        """This function returns the SHA-1 hash of the file passed into it"""

        # make a hash object
        h = hashlib.sha1()

        # open file for reading in binary mode
        with open(str(path), "rb") as file:
            # loop till the end of the file
            chunk = 0
            while chunk != b"":
                # read only 1024 bytes at a time
                chunk = file.read(1024)
                h.update(chunk)

        # return the hex representation of digest
        return h.hexdigest()

    def process_upload_path_segment(self, path: Path, segment: str):
        if segment.startswith("{now():"):
            return datetime.datetime.now().strftime(
                segment[segment.index(":") + 1 : -1]
            )
        elif segment.startswith("{filetimestamp:"):
            return datetime.datetime.fromtimestamp(path.stat().st_mtime).strftime(
                segment[segment.index(":") + 1 : -1]
            )
        return segment
