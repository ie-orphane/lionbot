from utils import Log
from typing import Literal, Dict, Tuple
from .__self__ import get_config


__all__ = ["get_user", "get_users"]


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
