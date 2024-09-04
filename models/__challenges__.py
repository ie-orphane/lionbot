import json
from models.__schema__ import Model
from utils import Language, Difficulty, Extension, Coin, Runner


class BaseChallenge(Model):
    BASE: str = "challenges"
    language: Language
    runner: Runner
    extension: Extension
    forbidden: list[str]

    @classmethod
    def read(cls, language: Language):
        for data in cls.read_all():
            if data.language == language:
                return data

    @classmethod
    def read_all(cls):
        with open(f"./data/{cls.BASE}.json", "r") as file:
            return [cls(**data) for data in json.load(file)]


class Test(Model):
    description: str
    args: list[str]
    expected: str


class ChallengeFields(BaseChallenge):
    name: str
    level: str
    _tests: list[dict]
    difficulty: Difficulty
    additionales: str = ""
    not_allowed: list[str] = []


class ChallengeData(ChallengeFields):
    MODEL = BaseChallenge
    BASE: str = "challenges"
    COINS: dict[Difficulty, Coin] = {"easy": 2, "medium": 43, "hard": 101}

    @classmethod
    def read(cls, language: Language, level: int | str):
        for data in cls.read_all(language):
            if data.level == int(level):
                return data

    @classmethod
    def read_all(cls, language: Language):
        model = cls.MODEL.read(language)
        with open(f"./data/{cls.BASE}/{language}.json", "r") as file:
            return [cls(**(model.__to_dict__()), **data) for data in json.load(file)]

    @property
    def coins(self) -> Coin:
        return self.COINS[self.difficulty]

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
