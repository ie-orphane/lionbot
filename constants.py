import math
from utils import Message, Color

__all__ = [
    "GOLDEN_RATIO",
    "BOT_COINS_AMOUNT",
    "OUTLIST_AMOUNT",
    "EXCLUDE_DIRS",
    "MESSAGE",
    "COLOR",
]

GOLDEN_RATIO = (1 + math.sqrt(5)) / 2

BOT_COINS_AMOUNT = GOLDEN_RATIO**29
OUTLIST_AMOUNT = GOLDEN_RATIO**11

MESSAGE = Message()
COLOR = Color()

EXCLUDE_DIRS = ["__pycache__", ".git", "venv"]
