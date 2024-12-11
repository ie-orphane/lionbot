from .__self__ import get_config, set_config
from utils import Log


__all__ = ["get_message", "set_message"]


def get_message(channel: str, message: str) -> int | None:
    messages: dict[str, int] = get_config(channel, "msgs")
    if messages is None:
        Log.error("Config", f"{channel} field not found in msgs")
        return None
    return messages.get(message)


def set_message(channel: str, message: int, message_id: int) -> None:
    messages: dict[str, int] = get_config(channel, "msgs")
    if messages is None:
        Log.error("Config", f"{channel} field not found in msgs")
        return
    messages[message] = message_id
    set_config(channel, messages, "msgs")
