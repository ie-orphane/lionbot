from env import BOT_TASKS
import json
from utils import Log
from discord.ext.tasks import Loop
from .__all__ import all_tasks


def start(bot) -> None:
    if BOT_TASKS != "ALL" and (
        not (BOT_TASKS.startswith("[") and BOT_TASKS.endswith("]"))
    ):
        Log.error("Tasks", "Invalid format of BOT_TASKS.")
        return

    tasks: list[tuple[str, Loop]] = []

    if BOT_TASKS == "ALL":
        tasks = list(all_tasks.items())
    elif BOT_TASKS.startswith("[") and BOT_TASKS.endswith("]"):
        try:
            tasks = [
                (task_name, task)
                for task_name, task in all_tasks.items()
                if task_name in json.loads(BOT_TASKS)
            ]
        except json.decoder.JSONDecodeError:
            Log.error("Tasks", "Failed to load BOT_TASKS.")
            return

    Log.info("Tasks", f"{len(tasks)} Task(s) Loaded.")

    for _, task in tasks:
        task.start(bot)
