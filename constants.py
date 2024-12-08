import math
from utils import Message, Color


GOLDEN_RATIO = (1 + math.sqrt(5)) / 2

BOT_COINS_AMOUNT = GOLDEN_RATIO**29
OUTLIST_AMOUNT = GOLDEN_RATIO**11

MESSAGE = Message()
COLOR = Color()

EXCLUDE_DIRS = ["__pycache__", ".git", "venv"]


# ------ config ------
CONFIG_FILE: str = "bot/config.json"


# Exlude files that should not be imported
EXLUDE_MODULE_FILES = ["__init__.py", "__all__.py", "__self__.py"]
