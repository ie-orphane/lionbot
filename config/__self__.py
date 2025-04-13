import os
import pprint
from typing import Any, Dict, Literal

import env
from utils import Log, open_file

__all__ = ["get_config", "set_config", "get_all"]


CONFIG_DIR: str = os.path.join(os.path.abspath(env.BASE_DIR), "config")
CONFIG_SUFFIX: str = "json"


class config:
    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {pprint.saferepr(object=self.__dict__)}"

    def __eq__(self, other: object) -> bool:
        return self.__dict__ == other.__dict__

    def __to_dict__(self):
        return self.__dict__


ConfigPrefix = Literal["global", "msgs", "leaderboard", "emojis", "users"]


file_data: Dict[str, Any] = {}
modified_datetime: Dict[str, float] = {}


def get_all(prefix: ConfigPrefix = "global") -> Any | None:
    global file_data
    global modified_datetime

    file_path = f"{CONFIG_DIR}/{prefix}.{CONFIG_SUFFIX}"

    if not os.path.exists(file_path):
        Log.error("Config", f"{os.path.relpath(file_path)}: no such file.")
        return

    if not os.path.isfile(file_path):
        Log.error("Config", f"{os.path.relpath(file_path)}: is not a regular file.")
        return

    if os.path.getmtime(file_path) != modified_datetime.get(prefix):
        file_data[prefix] = open_file(file_path)
        modified_datetime[prefix] = os.path.getmtime(file_path)
        Log.info("Config", f"{os.path.relpath(file_path)}: readed!")

    return file_data.get(prefix)


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
        Log.error("Config", f"{os.path.relpath(file_path)}: is not a regular file.")
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
        Log.error("Config", f"{os.path.relpath(file_path)}: is not a regular file.")
        return

    if (config_prefix not in file_data) or (config_prefix not in modified_datetime):
        Log.error("Config", f"{os.path.relpath(file_path)}: not found.")
        return

    file_data[config_prefix][attribute_name] = attribute_value

    open_file(file_path, file_data.get(config_prefix))

    modified_datetime[config_prefix] = os.path.getmtime(file_path)

    Log.info("Config", f"{os.path.relpath(file_path)}: updated!")
