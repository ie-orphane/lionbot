from datetime import UTC, datetime
from typing import Literal

from .__colorful__ import Color as clr


def log(
    type: Literal["Info", "Error", "Task"],
    color: Literal["red", "green", "yellow", "blue", "cyan"],
    name: str,
    message: str,
    /,
) -> None:
    print(
        clr.black(datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")),
        f"{getattr(clr, color)(type)}{' ' * (8 - len(type))}",
        clr.magenta(name),
        message,
    )


class Log:
    log = staticmethod(log)

    @staticmethod
    def info(name: str, message: str) -> None:
        log("INFO", "blue", name, message)

    @staticmethod
    def error(name: str, message: str) -> None:
        log("ERROR", "red", name, message)

    @staticmethod
    def warning(name: str, message: str) -> None:
        log("WARNING", "yellow", name, message)

    @staticmethod
    def job(name: str, message: str) -> None:
        log("JOB", "cyan", name, message)
