from .__self__ import get_config
from typing import Literal
from utils import log


__all__ = ["get_user"]


def get_user(user: Literal["owner"]) -> int | None:
    users: dict[str, int] = get_config("USERS")
    if users is None:
        log("Error", "red", "Config", "USERS field not found")
        return None
    return users.get(user)
