import logging
import os
from importlib.metadata import version
from pathlib import Path
from typing import Dict


def setup_root_logger(log_path: Path = None, log_level=logging.INFO):
    logger = logging.getLogger()

    if not logger.hasHandlers():
        logger.setLevel(log_level)
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s"
        )
        stream_handler.setFormatter(formatter)
        stream_handler.addFilter(
            type(
                "",
                (logging.Filter,),
                {"filter": staticmethod(lambda r: r.name.split(".")[0] != "botocore")},
            )
        )
        logger.addHandler(stream_handler)

    if len(logger.handlers) == 1:
        if log_path:
            from logging.handlers import RotatingFileHandler

            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = RotatingFileHandler(
                log_path, maxBytes=5000000, backupCount=20
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)


def get_dd_tags():
    return {
        "tags": {
            "event_source": os.environ.get(
                "HMD_REPO_NAME", "hmd-cli-librarian-sync-watcher"
            ),
            "event_source_version": version(
                os.environ.get("HMD_REPO_NAME", "hmd-cli-librarian-sync-watcher")
            ),
            "event_source_instance_name": os.environ.get(
                "HMD_INSTANCE_NAME", "default"
            ),
            "event_source_did": os.environ.get("HMD_DID", "default"),
            "event_source_cust_code": os.environ.get("HMD_CUSTOMER_CODE", "default"),
            "event_source_region": os.environ.get("HMD_REGION", "default"),
            "event_source_env": os.environ.get("HMD_ENVIRONMENT", "default"),
        }
    }


def build_dd_sender(logger):
    dd_base_url = os.environ.get("DD_BASE_URL")
    dd_api_key = os.environ.get("DD_API_KEY")
    if dd_api_key and dd_base_url:

        from hmd_cli_tools.hmd_cli_tools import send_datadog_event

        return send_datadog_event
    else:

        def noop(event_type: str, data: str, tags: Dict, ex=None):
            logger.info("Datadog not configured, skipping sending event")

        return noop
