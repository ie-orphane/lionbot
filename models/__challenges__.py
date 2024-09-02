import json
from models.__schema__ import Model
from utils import Language, Difficulty, Extension, Coin, Runner


class Test(Model):
    description: str
    args: list[str]
    expected: str


class ChallengeFields:
    name: str
    level: str
    _tests: list[dict]
    language: Language
    difficulty: Difficulty
    additionales: str = None
    forbidden: list[str] = None


class ChallengeData(Model, ChallengeFields):
    BASE: str = "challenges"
    COINS: dict[Difficulty, Coin] = {"easy": 2, "medium": 101, "hard": 199}
    EXTENSION: dict[Language, Extension] = {"shell": "sh"}
    RUNNER: dict[Language, Runner] = {"shell": "bash"}

    @classmethod
    def read(cls, language: Language, level: int | str):
        for data in cls.read_all(language):
            if data.level == int(level):
                return data

    @classmethod
    def read_all(cls, language: Language):
        with open(f"./data/{cls.BASE}.json", "r") as file:
            return [
                cls(language=language, **data) for data in json.load(file)[language]
            ]

    @property
    def extension(self) -> Extension:
        return self.EXTENSION[self.language]

    @property
    def coins(self) -> Coin:
        return self.COINS[self.difficulty]

    @property
    def runner(self) -> Runner:
        return self.RUNNER[self.language]

    @property
    def file(self) -> str:
        return f"{self.name}.{self.extension}"

    @property
    def tests(self) -> list[Test]:
        return [Test(**test) for test in self._tests]

    @property
    def text(self) -> str:
        with open(f"assets/subjects/{self.language}/{self.name}.ansi", "r") as file:
            return file.read()
