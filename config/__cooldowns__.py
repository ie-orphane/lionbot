from utils import Log
from .__self__ import get_config


__all__ = ["get_cooldown"]


def get_cooldown(
    cooldown: str,
    default: int = 0,
) -> int:
    cooldowns: dict[str, str] = get_config("COOLDOWNS")
    if cooldowns is None:
        Log.error("Config", "COOLDOWNS field not found")
        return default
    return cooldowns.get(cooldown.lower(), default)
