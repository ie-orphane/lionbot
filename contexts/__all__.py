import os
import importlib
import inspect
from utils import log


# Exlude files that should not be imported
EXLUDE_FILES = ["__init__.py", "__all__.py", "__self__.py"]


# Path to the directory containing the modules (relative to the current file)
modules_dir = os.path.dirname(__file__)

# Get a list of Python files (without extension) in contexts/
modules_name = [
    filename[:-3]
    for filename in os.listdir(modules_dir)
    if filename.endswith(".py") and filename not in EXLUDE_FILES
]

# Dynamically import the modules and store them into a dictionary
contexts = {}
for module_name in modules_name:
    # Dynamically import the module
    module = importlib.import_module(f".{module_name}", package=__package__)

    # Trancate the module name ('__module__' -> 'module')
    module_name = module_name.replace("_", "")

    # Add the module to the contexts dictionary
    # Assuming each module has a main function with the same name as the module
    try:
        module_func = getattr(module, module_name)
    except AttributeError:
        log("Warning", "yellow", "Context", f"cannot found {module_name} context function")
        continue

    if not inspect.iscoroutinefunction(module_func):
        log("Warning", "yellow", "Context", f"{module_name} is not an async function")
        continue

    postinal_argumets = inspect.signature(module_func).parameters
    postinal_argumets_count = len(postinal_argumets)

    if (postinal_argumets_count == 0):
        log("Warning", "yellow", "Context", f"{module_name} is missing a postinal argument")
        continue

    contexts[module_name] = (module_func, postinal_argumets_count)

# Update the __all__ list to include the dynamically imported modules
__all__ = list(contexts.keys())
