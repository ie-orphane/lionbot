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
from .__outlist__ import outlist


ALL_TASKS: dict[str, Callable[[commands.Bot], Coroutine]] = {
    "leaderboard": leaderboard,
    "weekly_data": weekly_data,
    "geek_of_the_week": geek_of_the_week,
    "deadline": deadline,
    "evaluations": evaluations,
    "outlist": outlist,
}



def start(bot: commands.Bot) -> None:
    load_dotenv(".env")
    TASKS: str | None = os.getenv("TASKS")

    if TASKS is None:
        bot.log("Error", clr.red, "Task", ".env missed TASKS")
        return

    if TASKS != "ALL" and (not (TASKS.startswith("[") and TASKS.endswith("]"))):
        bot.log("Error", clr.red, "Task", "invalid format of TASKS")
        return

    tasks: list = []

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
