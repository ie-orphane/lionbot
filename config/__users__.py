from typing import Dict, Literal

from utils import Log

from .__self__ import get_config

__all__ = ["get_user", "get_users"]


def get_user(_user: Literal["OWNER"]) -> int | None:
    user: Dict[str, int] = get_config(_user.upper(), "users")
    if user is None:
        Log.error("Config", f"{_user.upper()} field not found")
        return None
    return user


def get_users(
    _users: Literal["ADMINS", "COACHES", "HUNTERS", "PROS", "GEEKS"],
) -> list[int]:
    if (users := get_config(_users.upper(), "users")) is None:
        Log.error("Config", f"{_users.upper()} field not found")
        return []
    return users
