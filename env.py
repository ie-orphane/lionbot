import os
from dotenv import load_dotenv
from utils import Log


IS_MISSING: bool = False

TOKEN: str
TASKS: str
GITHUB_ACCESS_TOKEN: str


load_dotenv()

for env_variable_name in __annotations__:
    if globals().get(env_variable_name) is not None:
        continue

    if (env_variable := os.getenv(env_variable_name)) is None:
        Log.error("ENV", f"missing {env_variable_name}")
        IS_MISSING = True
        continue

    exec(f"{env_variable_name} = '{env_variable}'")
