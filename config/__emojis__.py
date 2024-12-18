from utils import Log
from typing import Literal
from .__self__ import get_config


__all__ = ["get_emoji"]


def get_emoji(emoji: Literal["coin", "star", "wakatime", "github", "portfolio"]) -> str:
    emojis: dict[str, str] = get_config("EMOJIS")
    if emojis is None:
        Log.error("Config", "EMOJIS field not found")
        return " "
    return emojis.get(emoji, " ")
