import env
import json
from discord.ext import commands
from utils import Log
from .__all__ import all_tasks


def start(bot: commands.Bot) -> None:
    if env.TASKS != "ALL" and (
        not (env.TASKS.startswith("[") and env.TASKS.endswith("]"))
    ):
        Log.error("Task", "invalid format of TASKS")
        return

    tasks: list = []

    if env.TASKS == "ALL":
        tasks = list(all_tasks.items())
    elif env.TASKS.startswith("[") and env.TASKS.endswith("]"):
        try:

            tasks = [
                (task_name, task)
                for task_name, task in all_tasks.items()
                if task_name in json.loads(env.TASKS)
            ]
        except json.decoder.JSONDecodeError:
            Log.error("Task", "failed to load tasks!")
            return

    Log.info("Task", f"{len(tasks)} Task(s) Loaded.")

    for _, task in tasks:
        task.start(bot)
