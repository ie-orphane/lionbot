import math
from utils import Message, Color
from typing import Literal


GOLDEN_RATIO = (1 + math.sqrt(5)) / 2

BOT_COINS_AMOUNT = GOLDEN_RATIO**29
OUTLIST_AMOUNT = GOLDEN_RATIO**11

MESSAGE = Message()
COLOR = Color()

EXCLUDE_DIRS = ["__pycache__", ".git", "venv"]


# ------ config ------
class Config:
    DIR: str = "bot"
    SUFFIX: str = "config.json"

    @property
    def path(self):
        return f"{self.DIR}/{self.FILE}"

    @classmethod
    def path(self, field: str):
        return f"{self.DIR}/{field}.{self.FILE}"


# ------ tasks ------
GITHUB_API_URL = "https://api.github.com"


class Quiz:
    START_TIME = 9, 30
    END_TIME = 23, 00
    CATEGORIES = ["bash", "React", "Laravel"]
    TAGS = ["BASH", "HTML", "Git", "JavaScript", "Python"]
    COLORS = {
        "bash": COLOR.green,
        "react": COLOR.cyan,
        "laravel": COLOR.red,
        "html": COLOR.orange,
        "git": COLOR.orange,
        "javascript": COLOR.yellow,
        "python": COLOR.blue,
    }
    REWARD_AMOUNT: dict[Literal["Easy", "Medium", "Hard"], int] = {
        "Easy": GOLDEN_RATIO * 1,
        "Medium": GOLDEN_RATIO * 1.5,
        "Hard": GOLDEN_RATIO * 2.5,
    }


# Exlude files that should not be imported
EXCLUDE_FILES = ["__init__.py", "__all__.py", "__self__.py"]

BUFFER_SLEEP_SECONDS = 60
