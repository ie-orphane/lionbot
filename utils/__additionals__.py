from typing import Literal

__all__ = [
    "Language",
    "Extension",
    "Difficulty",
    "Result",
    "Runner",
    "Social",
]

Language = Literal["bash"]
Extension = Literal["sh"]
Difficulty = Literal["easy", "medium", "hard"]
Result = Literal["OK", "KO", "ERROR", "TIMEOUT", "DEAD", "FORBIDDEN"]
Runner = Literal["bash"]
Social = Literal["github", "portfolio", "linkedin"]
