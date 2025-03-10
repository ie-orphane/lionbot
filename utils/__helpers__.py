import pickle
import json
import os
from .__colorful__ import Color as clr
from typing import Literal
from datetime import datetime, timedelta, date, UTC


__all__ = [
    "get_week",
    "open_file",
    "log",
    "get_files",
    "Week",
    "convert_seconds",
]


def convert_seconds(total_seconds: int) -> str:
    time_units = [
        ("y", 365 * 24 * 3600),
        ("mo", 30 * 24 * 3600),
        ("d", 24 * 3600),
        ("h", 3600),
        ("min", 60),
        ("s", 1),
    ]

    result = []
    for label, unit in time_units:
        if total_seconds >= unit:
            value, total_seconds = divmod(total_seconds, unit)
            result.append(f"{value}{label}")

    return " ".join(result)


def log(
    type: Literal["Info", "Error", "Task"],
    color: Literal["red", "green", "yellow", "blue", "cyan"],
    name: str,
    message: str,
):
    print(
        clr.black(datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")),
        f"{getattr(clr, color)(type)}{' ' * (8 - len(type))}",
        clr.magenta(name),
        message,
    )


def get_files(path: str, praser=int):
    return [praser(file[: file.index(".")]) for file in os.listdir(path)]


def open_file(file_path, data=None):
    file_extention = file_path.split(".")[-1]
    match file_extention:
        case "json":
            module = json
            write_mode = "w"
            read_mode = "r"
        case "pickle":
            module = pickle
            write_mode = "wb"
            read_mode = "rb"

    if data:
        with open(file_path, write_mode) as file:
            if file_extention == "json":
                module.dump(data, file, indent=2)
            else:
                module.dump(data, file)
            return

    with open(file_path, read_mode) as file:
        return module.load(file)


class Week:
    count: int
    start_date: date
    end_date: date

    def __init__(self, data: dict) -> None:
        self.__dict__ = data
        self.readable_start = str(self.start_date)
        self.readable_end = str(self.end_date)
        self.human_readable_start = f"{self.start_date:%d %b %Y}"
        self.human_readable_end = f"{self.end_date:%d %b %Y}"


def get_week(*, week_argument="last", end_date=None) -> Week | list:
    start_date = datetime(2023, 10, 23)
    end_date = end_date or datetime.utcnow()
    weeks: list[Week] = []

    current_date = start_date
    week_count = 1

    while current_date <= end_date:
        start_of_week = current_date - timedelta(days=current_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        weeks.append(
            Week(
                {
                    "count": week_count,
                    "start_date": start_of_week.date(),
                    "end_date": end_of_week.date(),
                }
            )
        )

        current_date += timedelta(days=7)
        week_count += 1

    match week_argument:
        case "beforelast":
            last_week = weeks[-2]
            return last_week
        case "last":
            last_week = weeks[-1]
            return last_week
        case "all":
            return weeks
        case _:
            return weeks[int(week_argument) - 1]
