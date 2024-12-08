from utils import Log
from typing import Literal
from .__self__ import get_config


__all__ = ["get_user"]


def get_user(user: Literal["owner"]) -> int | None:
    users: dict[str, int] = get_config("USERS")
    if users is None:
        Log.error("Config", "USERS field not found")
        return None
    return users.get(user)
