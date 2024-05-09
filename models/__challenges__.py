import json
from models.__schema__ import Model
from utils import RANKS


class ChallengeFields:
    id: str
    instructions: str
    input: str = None
    output: str
    coins: int
    points: int
    difficulty: str


class ChallengeData(Model, ChallengeFields):
    BASE: str = "challenges"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.__dict__.update(RANKS[self.rank].__dict__)

    @classmethod
    def read(cls, id: int | str):
        for data in cls.read_all():
            if data.id == int(id):
                return data

    @classmethod
    def read_all(cls):
        with open(f"./data/{cls.BASE}.json", "r") as file:
            return [cls(**data) for data in json.load(file)]
