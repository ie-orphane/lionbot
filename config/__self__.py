import os
import env
from utils import open_file, Log
from typing import Literal, Any, Dict


__all__ = ["get_config", "set_config"]


CONFIG_DIR: str = os.path.join(os.path.abspath(env.BASE_DIR), "config")
CONFIG_SUFFIX: str = "json"


ConfigPrefix = Literal["global", "msgs", "leaderboard"]


file_data: Dict[str, Any] = {}
modified_datetime: Dict[str, float] = {}


def get_config(
    attribute_name: str, config_prefix: ConfigPrefix = "global"
) -> Any | None:
    global file_data
    global modified_datetime

    file_path = f"{CONFIG_DIR}/{config_prefix}.{CONFIG_SUFFIX}"

    if not os.path.exists(file_path):
        Log.error("Config", f"{os.path.relpath(file_path)}: no such file.")
        return

    if not os.path.isfile(file_path):
        Log.error(
            "Config", f"{os.path.relpath(file_path)}: is not a regular file."
        )
        return

    if os.path.getmtime(file_path) != modified_datetime.get(config_prefix):
        file_data[config_prefix] = open_file(file_path)
        modified_datetime[config_prefix] = os.path.getmtime(file_path)
        Log.info("Config", f"{os.path.relpath(file_path)}: readed!")

    return file_data.get(config_prefix).get(attribute_name)


def set_config(
    attribute_name: str,
    attribute_value: Any,
    config_prefix: ConfigPrefix = "global",
) -> None:
    global file_data
    global modified_datetime

    file_path = f"{CONFIG_DIR}/{config_prefix}.{CONFIG_SUFFIX}"

    if not os.path.exists(file_path):
        Log.error("Config", f"{os.path.relpath(file_path)}: no such file.")
        return

    if not os.path.isfile(file_path):
        Log.error(
            "Config", f"{os.path.relpath(file_path)}: is not a regular file."
        )
        return

    if (config_prefix not in file_data) or (config_prefix not in modified_datetime):
        Log.error("Config", f"{os.path.relpath(file_path)}: not found.")
        return

    file_data[config_prefix][attribute_name] = attribute_value

    open_file(file_path, file_data.get(config_prefix))

    modified_datetime[config_prefix] = os.path.getmtime(file_path)

    Log.info("Config", f"{os.path.relpath(file_path)}: updated!")
