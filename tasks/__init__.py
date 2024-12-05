import os
import json
from discord.ext import commands
from dotenv import load_dotenv
from typing import Callable, Coroutine
from utils import clr

from .__leaderboard__ import leaderboard
from .__weekly_data__ import weekly_data
from .__geek_of_the_week__ import geek_of_the_week
from .__deadline__ import deadline
from .__evaluations__ import evaluations
from .__blacklist__ import blacklist


ALL_TASKS: dict[str, Callable[[commands.Bot], Coroutine]] = {
    "leaderboard": leaderboard,
    "weekly_data": weekly_data,
    "geek_of_the_week": geek_of_the_week,
    "deadline": deadline,
    "evaluations": evaluations,
    "blacklist": blacklist,
}

load_dotenv("./.env")

TASKS: str | None = os.getenv("TASKS")


def start(bot: commands.Bot) -> None:
    tasks: list = []

    if TASKS:
        if TASKS == "ALL":
            tasks = list(ALL_TASKS.items())
        elif TASKS.startswith("[") and TASKS.endswith("]"):
            try:

                tasks = [
                    (task_name, task)
                    for task_name, task in ALL_TASKS.items()
                    if task_name in json.loads(TASKS)
                ]
            except json.decoder.JSONDecodeError:
                bot.log("Error", clr.red, "Task", "failed to load tasks!")

    bot.log(
        "Info", clr.yellow, "Task", f"loading {", ".join(map(lambda x: x[0], tasks))}."
    )

    for _, task in tasks:
        task.start(bot)
