import importlib
import inspect
from pathlib import Path

from consts import EXCLUDE_DIRS, EXCLUDE_FILES
from utils import Log

from .__self__ import __NAME__, ctx

all_contexts: dict[str, ctx] = {}
modules_dir = Path(__file__).parent

for path, dirs, files in modules_dir.walk():
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    files = [
        f.removesuffix(".py")
        for f in files
        if f not in EXCLUDE_FILES and f.endswith(".py")
    ]

    for filename in files:
        base = []
        if path.name != "contexts":
            base = str(path).removeprefix(str(modules_dir) + "/").split("/")

        if (not filename.startswith("__")) or (not filename.endswith("__")):
            Log.error(__NAME__, f"{filename} not consired as a valid module")
            continue

        module_path = ".".join([""] + base + [filename])
        module_name = " ".join(base + [filename.strip("__")])

        module = importlib.import_module(module_path, package=__package__)

        module_desc: str | None = getattr(module, "__DESCRIPTION__", None)
        if (module_desc is not None) and (not isinstance(module_desc, str)):
            Log.error(
                __NAME__, f"Invalid: '{module_name}'.__DESCRIPTION__ must be a 'str'"
            )
            continue

        admin_only: bool = getattr(module, "__ADMIN_ONLY__", False)
        if not isinstance(admin_only, bool):
            Log.error(
                __NAME__, f"Invalid: '{module_name}'.__ADMIN_ONLY__ must be a 'bool'"
            )
            continue

        owner_only: bool = getattr(module, "__OWNER_ONLY__", False)
        if not isinstance(owner_only, bool):
            Log.error(
                __NAME__, f"Invalid: '{module_name}'.__OWNER_ONLY__ must be a 'bool'"
            )
            continue

        try:
            module_func = getattr(module, "__run__")
        except AttributeError:
            Log.error(__NAME__, f"Missing: '{module_name}'.__run__ not found")
            continue
        if not inspect.iscoroutinefunction(module_func):
            Log.error(
                __NAME__, f"Invalid: '{module_name}'.__run__ must be an 'async func'"
            )
            continue

        arguments = inspect.signature(module_func).parameters
        arguments_count = len(arguments)

        if "bot" not in arguments:
            Log.error(
                __NAME__,
                f"Missing: '{module_name}' required 'bot: commands.Bot' argument",
            )
            continue

        if "message" not in arguments:
            Log.error(
                __NAME__,
                f"Missing: '{module_name}' required 'message: discord.Message' argument",
            )
            continue

        invalid = False
        for name, param in arguments.items():
            if param.annotation is inspect._empty:
                invalid = True
                Log.error(
                    __NAME__, f"Missing: '{module_name}'.{name} required annotation"
                )
                break
            if param.kind != param.KEYWORD_ONLY:
                invalid = True
                Log.error(
                    __NAME__,
                    f"Invalid: '{module_name}'.{name} must be keyword-only",
                )
                break

        if invalid:
            continue

        all_contexts[module_name] = ctx(
            name=module_name,
            func=module_func,
            args=arguments,
            desc=module_desc,
            admin_only=admin_only,
            owner_only=owner_only,
        )

__all__ = list(all_contexts.keys())
