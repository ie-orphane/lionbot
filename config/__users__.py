from typing import Dict, Literal, Tuple

from utils import Log

from .__self__ import get_config

__all__ = ["get_user", "get_users", "get_owner", "get_admins"]


UserConfig = Literal["owner", "coach"]


def get_user(user: UserConfig) -> int | None:
    users: Dict[str, int] = get_config("USERS")
    if users is None:
        Log.error("Config", "USERS field not found")
        return None
    return users.get(user)


def get_users(*users: UserConfig, nullable: bool = True) -> Tuple[int | None]:
    _users: Dict[str, int] = get_config("USERS")
    if users is None:
        Log.error("Config", "USERS field not found")
        return ()
    return tuple(
        _users.get(user) for user in users if nullable or not (_users.get(user) is None)
    )


def get_owner() -> int | None:
    _users: Dict[str, int | list] = get_config("USERS")
    if _users is None:
        Log.error("Config", "USERS field not found")
        return None
    return _users.get("owner")


def get_admins() -> list[int]:
    _users: Dict[str, int | list] = get_config("USERS")
    if _users is None:
        Log.error("Config", "USERS field not found")
        return []
    return _users.get("admins", [])
