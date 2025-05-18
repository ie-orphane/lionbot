from typing import Dict, Literal

from utils import Log

from .__self__ import get_config, set_config

__all__ = ["get_user", "get_users", "set_user", "del_user"]


def get_user(_user: Literal["OWNER"]) -> int | None:
    user: Dict[str, int] = get_config(_user.upper(), "users")
    if user is None:
        Log.error("CONFIG.users", f"{_user.upper()} field not found")
        return None
    return user


def get_users(
    _users: Literal["ADMINS", "COACHES", "HUNTERS", "PROS", "GEEKS"],
) -> list[int]:
    if (users := get_config(_users.upper(), "users")) is None:
        Log.error("CONFIG.users", f"{_users.upper()} field not found")
        return []
    return users


def set_user(
    _id: int, _user: Literal["ADMINS", "COACHES", "HUNTERS", "PROS", "GEEKS"]
) -> bool | None:
    users = get_config(_user.upper(), "users")
    if users is None:
        Log.error("CONFIG.users", f"{_user.upper()} field not found")
        return None
    if _id in users:
        return False
    users.append(_id)
    set_config(_user.upper(), users, "users")
    return True


def del_user(
    _id: int, _user: Literal["ADMINS", "COACHES", "HUNTERS", "PROS", "GEEKS"]
) -> bool | None:
    users = get_config(_user.upper(), "users")
    if users is None:
        Log.error("CONFIG.users", f"{_user.upper()} field not found")
        return None
    if _id not in users:
        return False
    users.remove(_id)
    set_config(_user.upper(), users, "users")
    return True
