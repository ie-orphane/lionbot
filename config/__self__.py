import os
from utils import open_file, Log
from typing import Literal, Any, Dict
from consts import Config


__all__ = ["get_config", "set_config"]


ConfigAttribute = Literal[
    "GUILD",
    "REPOSITORY",
    "ROLES",
    "USERS",
    "CHANNELS",
    "EMOJIS",
    "REACTIONS",
    "EXTENSTIONS",
]

ConfigPrefix = Literal["global", "messages", "leaderboard"]


file_data: Dict[str, Any] = {}
modified_datetime: Dict[str, float] = {}


def get_config(
    attribute_name: ConfigAttribute, config_prefix: ConfigPrefix = "global"
) -> Any | None:
    global file_data
    global modified_datetime

    config_file_path = f"{Config.DIR}/{config_prefix}.{Config.SUFFIX}"

    if not os.path.exists(config_file_path):
        Log.error("Config", f"{config_file_path}: no such file.")
        return

    if not os.path.isfile(config_file_path):
        Log.error("Config", f"{config_file_path}: is not a regular file.")
        return

    if os.path.getmtime(config_file_path) != modified_datetime.get(config_prefix):
        file_data[config_prefix] = open_file(config_file_path)
        modified_datetime[config_prefix] = os.path.getmtime(config_file_path)
        Log.info("Config", f"{config_file_path}: readed!")

    return file_data.get(config_prefix).get(attribute_name)


def set_config(
    attribute_name: ConfigAttribute,
    attribute_value: Any,
    config_prefix: ConfigPrefix = "global",
) -> None:
    global file_data
    global modified_datetime

    config_file_path = f"{Config.DIR}/{config_prefix}.{Config.SUFFIX}"

    if not os.path.exists(config_file_path):
        Log.error("Config", f"{config_file_path}: no such file.")
        return

    if not os.path.isfile(config_file_path):
        Log.error("Config", f"{config_file_path}: is not a regular file.")
        return

    if (config_prefix not in file_data) or (config_prefix not in modified_datetime):
        Log.error("Config", f"{config_file_path}: not found.")
        return

    file_data[config_prefix][attribute_name] = attribute_value

    open_file(config_file_path, file_data.get(config_prefix))

    modified_datetime[config_prefix] = os.path.getmtime(config_file_path)

    Log.info("Config", f"{config_file_path}: updated!")
