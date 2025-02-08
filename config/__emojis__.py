from utils import Log
from typing import Literal
from .__self__ import get_config


__all__ = ["get_emoji", "get_reaction"]


def get_emoji(
    emoji: Literal["coin", "star", "wakatime", "github", "portfolio"],
    default: str | None = " ",
) -> str | None:
    emojis: dict[str, str] = get_config("EMOJIS")
    if emojis is None:
        Log.error("Config", "EMOJIS field not found")
        return default
    return emojis.get(emoji.lower(), default)


def get_reaction(
    reaction: str,
    default: str | None = " ",
) -> str | None:
    reactions: dict[str, str] = get_config("REACTIONS")
    if reactions is None:
        Log.error("Config", "REACTIONS field not found")
        return default
    return reactions.get(reaction.lower(), default)
