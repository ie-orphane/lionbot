import os
from utils import open_file, Log
from typing import Literal, Any
from constants import Config


__all__ = ["get_config"]


ConfigAttribute = Literal["GUILD", "USERS", "CHANNELS", "EMOJIS", "EXTENSTIONS"]


file_data: dict[str, Any] = {}
modified_datetime: dict[str, float] = {}


def get_config(
    attribute_name: ConfigAttribute, config_prefix: str = "global"
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
