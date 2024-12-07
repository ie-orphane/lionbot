import os
from utils import open_file, log
from typing import Literal, Any
from constants import CONFIG_FILE


__all__ = ["get_config"]


ConfigAttribute = Literal["GUILD", "USERS", "CHANNELS", "EMOJIS", "EXTENSTIONS"]


file_data: dict | None = None
modified_datetime: float | None = None


def get_config(attribute_name: ConfigAttribute) -> Any | None:
    global file_data
    global modified_datetime

    if not file_data:
        file_data = open_file(CONFIG_FILE)
        log("Info", "cyan", "Config", f"{CONFIG_FILE}: intial read.")

    if not modified_datetime:
        modified_datetime = os.path.getmtime(CONFIG_FILE)
        log("Info", "cyan", "Config", f"{CONFIG_FILE}: modified datetime updated!")

    if os.path.getmtime(CONFIG_FILE) != modified_datetime:
        file_data = open_file(CONFIG_FILE)
        modified_datetime = os.path.getmtime(CONFIG_FILE)
        log("Info", "cyan", "Config", f"{CONFIG_FILE}: reread!")

    return file_data.get(attribute_name)
