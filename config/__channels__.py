from typing import Literal
from .__self__ import get_config


__all__ = ["get_channel"]


def get_channel(
    channel: Literal["welcome", "challenges", "blacklist_event"]
) -> int | None:
    channels: dict[str, int] = get_config("CHANNELS")
    if channels is None:
        return None
    return channels.get(channel)
