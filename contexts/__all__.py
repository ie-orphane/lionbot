import os
import importlib
import inspect
from utils import Log
from consts import EXLUDE_MODULE_FILES


# Path to the directory containing the modules (relative to the current file)
modules_dir = os.path.dirname(__file__)

# Get a list of Python files (without extension) in contexts/
modules_name = [
    filename[:-3]
    for filename in os.listdir(modules_dir)
    if filename.endswith(".py") and filename not in EXLUDE_MODULE_FILES
]

# Dynamically import the modules and store them into a dictionary
all_contexts = {}
for module_name in modules_name:
    if (not module_name.startswith("__")) or (not module_name.endswith("__")):
        Log.warning("Context", f"{module_name} not consired as a valid module")
        continue

    # Dynamically import the module
    module = importlib.import_module(f".{module_name}", package=__package__)

    # Trancate the module name ('__module__' -> 'module')
    module_name = module_name.replace("_", "")

    # Add the module to the all_contexts dictionary
    # Assuming each module has a main function with the same name as the module
    try:
        module_func = getattr(module, module_name)
    except AttributeError:
        Log.warning("Context", f"cannot found {module_name} context function")
        continue

    if not inspect.iscoroutinefunction(module_func):
        Log.warning("Context", f"{module_name} is not an async function")
        continue

    postinal_argumets = inspect.signature(module_func).parameters
    postinal_argumets_count = len(postinal_argumets)

    if postinal_argumets_count == 0:
        Log.warning("Context", f"{module_name} is missing a postinal argument")
        continue

    all_contexts[module_name] = (module_func, postinal_argumets_count)

# Update the __all__ list to include the dynamically imported modules
__all__ = list(all_contexts.keys())
