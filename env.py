"""
load and store enviroment variables from the .env

### Raises:
- `AttributeError`: if env variable not found
"""

import os

from dotenv import load_dotenv

from utils import Log

IS_MISSING: bool = False

DISCORD_BOT_TOKEN: str

BOT_TASKS: str
BOT_COGS: str

BASE_DIR: str

QUIZ_API_URL: str
QUIZ_API_KEY: str
WAKATIME_BASE_URL: str
WAKATIME_API_URL: str


load_dotenv()

for env_variable_name in __annotations__:
    if globals().get(env_variable_name) is not None:
        continue

    if ((env_variable := os.getenv(env_variable_name)) is None) or (env_variable == ""):
        Log.error("ENV", f"missing {env_variable_name}")
        IS_MISSING = True
        continue

    exec(f"{env_variable_name} = '{env_variable}'")
