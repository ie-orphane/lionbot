from typing import Literal

import env
from consts import GOLDEN_RATIO
from notations import CHALLENGE

from .__self__ import config, get_config

__all__ = [
    "get_challenges",
    "get_challenge_by_level",
    "get_challenge_by_id",
    "get_challenge_by_name",
]


class _test(config):
    description: str
    args: list[str]
    expected: str


class challenge(config):
    """challenge config class.
    Attributes:
        id (`str`): The ID of the challenge.
        language (`str`): The language of the challenge.
        forbidden (`list`): List of forbidden commands/functions/libraries.
        extension (`str`): The file extension for the challenge.
        runner (`str`): The runner for the challenge.
        name (`str`): The name of the challenge.
        level (`str`): The level of the challenge.
        _tests (`list`): The tests for the challenge.
        difficulty (`str`): The difficulty level of the challenge.
        additionales (`str`): Additional code for the challenge.
        not_allowed (`list`): List of not allowed commands/functions/libraries.
        coins (`float`): The number of coins for the challenge's reward.
        file (`str`): The filename of the challenge.
        tests (`list`[`test`]): The tests for the challenge.
        subject (`str`): The subject of the challenge.
    """

    runner: CHALLENGE.RUNNER
    extension: CHALLENGE.EXTENSION
    forbidden: list[str]
    COINS: dict[CHALLENGE.DIFFICULTY, float] = {
        "easy": GOLDEN_RATIO * 2,
        "medium": GOLDEN_RATIO * 29,
        "hard": GOLDEN_RATIO * 67,
    }

    id: str
    name: str
    level: str
    language: str
    _tests: list[dict]
    difficulty: CHALLENGE.DIFFICULTY
    additionales: str = ""
    not_allowed: list[str] = []

    @property
    def coins(self) -> float:
        return self.COINS[self.difficulty]

    @property
    def file(self) -> str:
        return f"{self.name}.{self.extension}"

    @property
    def tests(self) -> list[_test]:
        return [_test(**test) for test in self._tests]

    @property
    def subject(self) -> str:
        with open(
            f"{env.BASE_DIR}/storage/subjects/{self.language}/{self.name}.ansi"
        ) as file:
            return file.read()


def get_challenges(language: Literal["SHELL"]) -> list[challenge]:
    """
    Get all challenges for a given language.
    Args:
        language (`str`): The language to get challenges for.
    Returns:
        `list`[`challenge`]: A list of challenges for the given language.
    """
    if (
        ((challenges := get_config(language.upper(), "challenges")) is None)
        or ((globals_ := challenges.get("globals")) is None)
        or ((locals_ := challenges.get("locals")) is None)
    ):
        return None
    return [
        challenge(**globals_, **local, language=language.lower(), level=level)
        for level, local in enumerate(locals_)
    ]


def get_challenge_by_level(language: Literal["BASH"], level: int) -> challenge | None:
    r"""
    Get a challenge for a given language and level.
    Args:
        language (`str`): The language to get the challenge for.
        level (`int`): The level of the challenge to get.
    Returns:
        `challenge` | `None`: The challenge for the given language and level, or None if not found.
    """
    challenges: dict[Literal["globals", "locals"], dict | list]

    if (
        ((challenges := get_config(language.upper(), "challenges")) is None)
        or ((globals_ := challenges.get("globals")) is None)
        or ((locals_ := challenges.get("locals")) is None)
        or (level >= len(locals_))
    ):
        return None

    return challenge(
        **globals_, **locals_[level], language=language.lower(), level=level
    )


def get_challenge_by_id(language: Literal["BASH"], id: str) -> challenge | None:
    r"""
    Get a challenge for a given language and id.
    Args:
        language (`str`): The language to get the challenge for.
        id (`str`): The ID of the challenge to get.
    Returns:
        `challenge` | `None`: The challenge for the given language and id, or None if not found.
    """
    challenges: dict[Literal["globals", "locals"], dict | list]

    if (
        ((challenges := get_config(language.upper(), "challenges")) is None)
        or ((globals_ := challenges.get("globals")) is None)
        or ((locals_ := challenges.get("locals")) is None)
    ):
        return None

    for level, local in enumerate(locals_):
        if local["id"] == id:
            return challenge(
                **globals_, **local, language=language.lower(), level=level
            )

    return None


def get_challenge_by_name(
    language: Literal["BASH", "JAVASCRIPT"], name: str
) -> challenge | None:
    r"""
    Get a challenge for a given language and name.
    Args:
        language (`str`): The language to get the challenge for.
        name: `str`: The name of the challenge to get.
    Returns:
        `challenge` | `None`: The challenge for the given language and name, or None if not found.
    """
    challenges: dict[Literal["globals", "locals"], dict | list]

    if (
        ((challenges := get_config(language.upper(), "challenges")) is None)
        or ((globals_ := challenges.get("globals")) is None)
        or ((locals_ := challenges.get("locals")) is None)
    ):
        return None

    for level, local in enumerate(locals_):
        if local["name"] == name:
            return challenge(
                **globals_, **local, language=language.lower(), level=level
            )

    return None
