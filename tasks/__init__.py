import os
import json
from discord.ext import commands
from dotenv import load_dotenv
from .__all__ import all_tasks
from utils import log, Log


def start(bot: commands.Bot) -> None:
    load_dotenv(".env")
    TASKS: str | None = os.getenv("TASKS")

    if TASKS is None:
        Log.error("Task", ".env missed TASKS")
        return

    if TASKS != "ALL" and (not (TASKS.startswith("[") and TASKS.endswith("]"))):
        Log.error("Task", "invalid format of TASKS")
        return

    tasks: list = []

    if TASKS == "ALL":
        tasks = list(all_tasks.items())
    elif TASKS.startswith("[") and TASKS.endswith("]"):
        try:

            tasks = [
                (task_name, task)
                for task_name, task in all_tasks.items()
                if task_name in json.loads(TASKS)
            ]
        except json.decoder.JSONDecodeError:
            Log.error("Task", "failed to load tasks!")
            return

    Log.info("Task", f"{len(tasks)} Task(s) Loaded.")

    for _, task in tasks:
        task.start(bot)
