from typing import Literal


class CHALLENGE:
    """
    Definitions of the notations used in the challenge.
    Attributes:
        LANGUAGE (Literal): The language of the challenge.
        EXTENSION (Literal): The file extension of the challenge.
        DIFFICULTY (Literal): The difficulty level of the challenge.
        RESULT (Literal): The result of the challenge.
        RUNNER (Literal): The runner for the challenge.
    """

    """LANGUAGE: The language of the challenge."""
    LANGUAGE = Literal["bash", "javascript"]
    """EXTENSION: The file extension of the challenge."""
    EXTENSION = Literal["sh", "js"]
    """DIFFICULTY: The difficulty level of the challenge."""
    DIFFICULTY = Literal["easy", "medium", "hard"]
    """RESULT: The result of the challenge."""
    RESULT = Literal["OK", "KO", "ERROR", "TIMEOUT", "DEAD", "FORBIDDEN"]
    """RUNNER: The runner for the challenge."""
    RUNNER = Literal["bash", "bun"]


"""SOCIAL: The social media platforms."""
SOCIAL = Literal["github", "portfolio", "linkedin"]

"""EMBLEM: The achievement emblems."""
EMBLEM = Literal["geeks", "admins", "hunters", "coaches", "pros"]
