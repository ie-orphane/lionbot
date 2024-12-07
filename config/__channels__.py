from typing import Literal
from .__self__ import get_config


__all__ = ["get_channel", "ConfigChannel"]

ConfigChannel = Literal["welcome", "challenges", "blacklist_event"]


def get_channel(channel: ConfigChannel) -> int | None:
    channels: dict[str, int] = get_config("CHANNELS")
    if channels is None:
        return None
    return channels.get(channel)
