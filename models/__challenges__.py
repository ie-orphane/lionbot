import json
from models.__schema__ import Model
from utils import Language, EXTENSION


class Test:
    description: str
    args: list[str]
    expected: str

    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)


class ChallengeFields:
    name: str
    level: str
    text: str
    language: Language
    tests: list[Test]
    additionales: str = None
    forbidden: list[str] = None
    coins: int = 269
    file: str
    exe: str


class ChallengeData(Model, ChallengeFields):
    BASE: str = "challenges"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.file = f"{self.name}.{self.exe}"
        self.tests = [Test(**test) for test in self.tests]
        with open(f"assets/subjects/{self.language}/{self.name}.txt", "r") as file:
            self.text = file.read()

    @classmethod
    def read(cls, language: Language, level: int | str):
        for data in cls.read_all(language):
            if data.level == int(level):
                return data

    @classmethod
    def read_all(cls, language: Language):
        with open(f"./data/{cls.BASE}.json", "r") as file:
            return [
                cls(language=language, exe=EXTENSION[language], **data)
                for data in json.load(file)[language]
            ]
