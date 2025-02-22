from typing import Literal

__all__ = [
    "Language",
    "Extension",
    "Difficulty",
    "Coin",
    "Result",
    "Runner",
    "Social",
]

Language = Literal["shell"]
Extension = Literal["sh"]
Difficulty = Literal["easy", "medium", "hard"]
Coin = Literal[2, 43, 101]
Result = Literal["OK", "KO", "ERROR", "TIMEOUT", "DEAD", "FORBIDDEN"]
Runner = Literal["bash"]
Social = Literal["github", "portfolio", "linkedin"]
