import json
import os
from pathlib import Path

from jsonschema import ValidationError, validate


def get_schema():
    """This function loads the given schema available"""
    schema_path = Path(__file__).parent / "config_schema.json"
    if os.environ.get("HMD_LIBRARIAN_SYNC_CONFIG_SCHEMA"):
        return json.loads(os.environ.get("HMD_LIBRARIAN_SYNC_CONFIG_SCHEMA"))
    elif schema_path.exists():
        with schema_path.open("r") as file:
            return json.load(file)
    else:
        raise Exception("Librarian sync configuration schema not found.")


def load_and_validate_config(instance_config, validate: bool):
    if os.path.isfile(instance_config):
        with instance_config.open("r") as config_data:
            config = json.loads(config_data.read())
    else:
        config = json.loads(os.environ.get("HMD_LIBRARIAN_SYNC_WATCHER_CONFIG"))
    if validate:
        return validate_config(config)
    else:
        return config


def validate_config(config):
    schema = get_schema()
    try:
        validate(instance=config, schema=schema)
    except ValidationError as err:
        return False, err

    message = "Given JSON data is Valid"
    return True, message
