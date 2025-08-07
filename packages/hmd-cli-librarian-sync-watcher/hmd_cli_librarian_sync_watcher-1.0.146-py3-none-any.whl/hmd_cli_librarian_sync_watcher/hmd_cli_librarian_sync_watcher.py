import asyncio
import logging
import os
from pathlib import Path

from hmd_cli_tools.hmd_cli_tools import get_env_var
from hmd_entity_storage import SqliteEngine
from hmd_graphql_client.hmd_db_engine_client import DbEngineClient
from hmd_lang_librarian_sync.hmd_lang_librarian_sync_client import (
    HmdLangLibrarianSyncClient,
    get_client_schema_root,
)
from hmd_lib_librarian_client.hmd_lib_librarian_client import HmdLibrarianClient
from hmd_lib_auth.hmd_lib_auth import okta_service_account_token_by_secret_name
from hmd_schema_loader import DefaultLoader

from .config.validate_config import load_and_validate_config
from .log import build_dd_sender, get_dd_tags
from .source_handlers import make_source

logger = logging.getLogger(__name__)
send_datadog_event = build_dd_sender(logger)
OKTA_SECRET_NAME = "okta-agent-service"


class LibrarianSyncWatcher:
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
        self, schema_location, db_location
    ) -> HmdLangLibrarianSyncClient:
        loader = DefaultLoader(base=os.path.expandvars(schema_location))
        engine = SqliteEngine(os.path.expandvars(db_location))
        db_client = DbEngineClient(engine, loader)
        return HmdLangLibrarianSyncClient(db_client)

    def __init__(self, instance_config):
        self.hmd_home = Path(os.path.expandvars(get_env_var("HMD_HOME")))
        hmd_repo_home = get_env_var("HMD_REPO_HOME", False)
        if hmd_repo_home:
            self.hmd_repo_home = Path(os.path.expandvars(hmd_repo_home))
        else:
            self.hmd_repo_home = None
        os.environ["HMD_INSTANCE_NAME"] = os.environ.get("HMD_INSTANCE_NAME", "agent")
        self.schema_uri = None
        schema_uri = get_env_var("SCHEMA_URI", False)
        if schema_uri:
            self.schema_uri = Path(schema_uri)
        schema_location = self.__resolve_schema_location()
        db_location = self.__ensure_db()
        librarian_sync_client = self.__build_client(schema_location, db_location)
        self.instance_config = instance_config

        if os.path.isfile(self.instance_config):
            self.abs_config_path = Path((Path.cwd() / self.instance_config).absolute())
            config = load_and_validate_config(self.abs_config_path, validate=False)
        else:
            config = load_and_validate_config(self.instance_config, validate=False)

        self.manifest_nid = os.environ.get("HMD_ENTITY_NID")
        for librarian in config["librarians"]:
            if config["librarians"][librarian].get("url") == "default":
                url = os.environ.get(f"HMD_{librarian.upper()}_LIBRARIAN_URL")
                if url:
                    config["librarians"][librarian]["url"] = url
                else:
                    raise Exception(
                        f"Librarian {librarian} is not configured with an url endpoint."
                    )
            if config["librarians"][librarian].get("api_key"):
                key = os.environ.get(f"HMD_{librarian.upper()}_LIBRARIAN_KEY")
                config["librarians"][librarian]["api_key"] = (
                    key if key != "default" else None
                )
            else:
                if self.manifest_nid:
                    try:
                        auth_token = okta_service_account_token_by_secret_name(
                            OKTA_SECRET_NAME
                        )
                        config["librarians"][librarian]["auth_token"] = auth_token
                    except Exception as e:
                        raise Exception(
                            f"Error retrieving auth token for {librarian}: {e}"
                        )

        self._config = config

        def make_librarian_client(config):
            return HmdLibrarianClient(
                base_url=config.get("url"),
                api_key=config.get("api_key"),
                auth_token=config.get("auth_token"),
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
                return librarian_clients[source_config.get("source")]
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
            ),
            self._config["sources"].items(),
        )

        self.sources = list(filter(lambda x: x.is_enabled, all_sources))
        self._watcher_tasks = []

    async def watch(self):
        tasks = list(
            map(lambda source: asyncio.create_task(source.start()), self.sources)
        )

        self._watcher_tasks = tasks
        await asyncio.gather(*self._watcher_tasks)

    def sync(self):
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
        logger.debug(f"Config: {self._config}")
        send_datadog_event(
            event_type="success",
            data="Librarian sync watcher configured successfully",
            tags=get_dd_tags(),
        )
        try:
            logger.info("Running sync")
            for source in self.sources:
                source.sync()
        except BaseException as e:
            logger.error("Watcher failed", exc_info=e)
            send_datadog_event(
                event_type="error",
                data=f"Librarian Sync Watcher failed during sync",
                ex=str(e),
                tags=get_dd_tags(),
            )
            raise e

    def start(self):
        try:
            logger.info("Starting watcher")
            asyncio.run(self.watch())
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
        for task in self._watcher_tasks:
            task.cancel()
        logger.info("all tasks stopped")
        send_datadog_event(
            event_type="info", data="Librarian sync watcher stopped", tags=get_dd_tags()
        )
