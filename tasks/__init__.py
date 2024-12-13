import env
import json
from discord.ext import commands
from utils import Log
from .__all__ import all_tasks


def start(bot: commands.Bot) -> None:
    if env.BOT_TASKS != "ALL" and (
        not (env.BOT_TASKS.startswith("[") and env.BOT_TASKS.endswith("]"))
    ):
        Log.error("Task", "invalid format of TASKS")
        return

    tasks: list = []

    if env.BOT_TASKS == "ALL":
        tasks = list(all_tasks.items())
    elif env.BOT_TASKS.startswith("[") and env.BOT_TASKS.endswith("]"):
        try:

            tasks = [
                (task_name, task)
                for task_name, task in all_tasks.items()
                if task_name in json.loads(env.BOT_TASKS)
            ]
        except json.decoder.JSONDecodeError:
            Log.error("Task", "failed to load tasks!")
            return

    Log.info("Task", f"{len(tasks)} Task(s) Loaded.")

    for _, task in tasks:
        task.start(bot)
