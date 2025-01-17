"""
load and store enviroment variables from the .env

### Raises:
- AttributeError: if env variable not found
"""

import os
from dotenv import load_dotenv
from utils import Log


IS_MISSING: bool = False

DISCORD_BOT_TOKEN: str
BOT_TASKS: str
GITHUB_ACCESS_TOKEN: str
QUIZ_API_ENDPOINT: str
QUIZ_API_KEY: str
WAKATIME_ENDPOINT: str


load_dotenv()

for env_variable_name in __annotations__:
    # checks if the variable not already stored
    if globals().get(env_variable_name) is not None:
        continue

    # checks the existant of the variable in .env
    if (env_variable := os.getenv(env_variable_name)) is None:
        Log.error("ENV", f"missing {env_variable_name}")
        IS_MISSING = True
        continue

    # store the variable in the module
    exec(f"{env_variable_name} = '{env_variable}'")
