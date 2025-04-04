import os
import importlib
import inspect
from utils import Log
from consts import EXCLUDE_FILES
from types import MappingProxyType


class Context:
    def __init__(
        self, *, name, func, args: MappingProxyType[str, inspect.Parameter], desc: str
    ):
        self.args: dict[str, inspect.Parameter] = {
            name: param
            for name, param in args.items()
            if name not in ("message", "bot")
        }
        self.func = func
        self.name = name
        self.desc = desc

    async def __call__(self, **options):
        return await self.func(**options)


# Path to the directory containing the modules (relative to the current file)
modules_dir = os.path.dirname(__file__)

# Get a list of Python files (without extension) in contexts/
modules_name = [
    filename[:-3]
    for filename in os.listdir(modules_dir)
    if filename.endswith(".py") and filename not in EXCLUDE_FILES
]

# Dynamically import the modules and store them into a dictionary
all_contexts: dict[str, Context] = {}
for module_name in modules_name:
    if (not module_name.startswith("__")) or (not module_name.endswith("__")):
        Log.warning("Context", f"{module_name} not consired as a valid module")
        continue

    # Dynamically import the module
    module = importlib.import_module(f".{module_name}", package=__package__)

    # Trancate the module name ('__module__' -> 'module')
    module_name = module_name.strip("_")

    # Add the module to the all_contexts dictionary
    try:
        module_func = getattr(module, "run")
    except AttributeError:
        Log.warning("Context", f"Missing run function: {module_name}")
        continue

    module_desc = None
    try:
        module_desc = getattr(module, "description")
    except AttributeError:
        Log.warning("Context", f"Missing description: {module_name}")
    module_desc = module_desc or ""

    if not inspect.iscoroutinefunction(module_func):
        Log.warning("Context", f"{module_name} is not an async function")
        continue

    arguments = inspect.signature(module_func).parameters
    arguments_count = len(arguments)

    if "bot" not in arguments:
        Log.warning(
            "Context",
            f"bot: discord.ext.commands.Bot argument missing in '{module_name}'",
        )
        continue

    if "message" not in arguments:
        Log.warning(
            "Context", f"message: discord.Message argument missing in '{module_name}'"
        )
        continue

    invalid = False
    for name, param in arguments.items():
        if param.annotation is inspect._empty:
            invalid = True
            Log.warning(
                "Context", f"'{name}' argument missing annotation in '{module_name}'"
            )
            break
        if param.kind != param.KEYWORD_ONLY:
            invalid = True
            Log.warning(
                "Context",
                f"'{name}' argument must be keyword-only in '{module_name}'",
            )
            break

    if invalid:
        continue

    all_contexts[module_name] = Context(
        name=module_name,
        func=module_func,
        args=arguments,
        desc=module_desc,
    )

# Update the __all__ list to include the dynamically imported modules
__all__ = list(all_contexts.keys())
