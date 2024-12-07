from typing import Literal
from .__self__ import get_config
from utils import log


__all__ = ["get_channel", "check_channels"]

ConfigChannel = Literal["welcome", "challenges", "outlist_event"]


def get_channel(channel: ConfigChannel) -> int | None:
    channels: dict[str, int] = get_config("CHANNELS")
    if channels is None:
        log("Error", "red", "Config", "CHANNELS field not found")
        return None
    return channels.get(channel)


def check_channels() -> str | None:
    for channel in ConfigChannel.__args__:
        if get_channel(channel) is None:
            return channel
