from typing import Dict, Literal

from utils import Log

from .__self__ import get_config

__all__ = ["get_user", "get_users"]


def get_user(user: Literal["owner"]) -> int | None:
    users: Dict[str, int] = get_config("USERS")
    if users is None:
        Log.error("Config", "USERS field not found")
        return None
    return users.get(user)


def get_users(prefix: Literal["admins", "coachs"]) -> list[int]:
    _users: Dict[str, int] = get_config("USERS")
    if _users is None:
        Log.error("Config", "USERS field not found")
        return []
    return _users.get(prefix)
