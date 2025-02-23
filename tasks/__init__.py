import env
import json
from utils import Log
from discord.ext.tasks import Loop
from .__all__ import all_tasks


def start(bot) -> None:
    if env.BOT_TASKS != "ALL" and (
        not (env.BOT_TASKS.startswith("[") and env.BOT_TASKS.endswith("]"))
    ):
        Log.error("Tasks", "Invalid format of env.BOT_TASKS.")
        return

    tasks: list[tuple[str, Loop]] = []

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
            Log.error("Tasks", "Failed to load env.BOT_TASKS.")
            return

    Log.info("Tasks", f"{len(tasks)} Task(s) Loaded.")

    for _, task in tasks:
        task.start(bot)
