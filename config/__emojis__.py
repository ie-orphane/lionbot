from typing import Literal

from utils import Log

from .__self__ import get_config

__all__ = ["get_emoji", "get_reaction", "get_extension", "get_emblem"]


def get_emoji(
    emoji: Literal["coin", "star", "wakatime", "github", "portfolio"],
    default: str | None = " ",
) -> str | None:
    emojis: dict[str, str] = get_config("EMOJIS", "emojis")
    if emojis is None:
        Log.error("Config", "EMOJIS field not found")
        return default
    return emojis.get(emoji.lower(), default)


def get_reaction(
    reaction: str,
    default: str | None = " ",
) -> str | None:
    reactions: dict[str, str] = get_config("REACTIONS", "emojis")
    if reactions is None:
        Log.error("Config", "REACTIONS field not found")
        return default
    return reactions.get(reaction.lower(), default)


def get_extension(extension: str) -> str:
    extensions: dict[str, str] = get_config("EXTENSIONS", "emojis")
    if extensions is None:
        Log.error("Config", "EXTENSIONS field not found")
        return extension
    return extensions.get(extension, extension)


def get_emblem(emblem: str, default: str | None = "") -> str | None:
    emblems: dict[str, str] = get_config("EMBLEMS", "emojis")
    if emblems is None:
        Log.error("Config", "EMBLEMS field not found")
        return default
    return emblems.get(emblem.lower(), default)
