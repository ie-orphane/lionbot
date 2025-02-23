import os
import importlib
import inspect
from utils import Log
from consts import EXCLUDE_FILES


modules_dir = os.path.dirname(__file__)


modules_name = [
    filename[:-3]
    for filename in os.listdir(modules_dir)
    if filename.endswith(".py") and filename not in EXCLUDE_FILES
]


all_tasks = {}
for module_name in modules_name:
    if (not module_name.startswith("__")) or (not module_name.endswith("__")):
        Log.warning("Task", f"{module_name} not consired as a valid module")
        continue

    module = importlib.import_module(f".{module_name}", package=__package__)

    module_name = module_name.removeprefix("__").removesuffix("__")

    try:
        module_func = getattr(module, module_name)
    except AttributeError:
        Log.warning("Task", f"cannot found {module_name} task function")
        continue

    postinal_argumets = inspect.signature(module_func.coro).parameters
    postinal_argumets_count = len(postinal_argumets)

    if postinal_argumets_count == 0:
        Log.warning("Task", f"{module_name} is missing a postinal argument")
        continue

    all_tasks[module_name] = module_func


__all__ = list(all_tasks.keys())
