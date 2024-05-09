import os
import json
from models.__schema__ import Model


class ChallengeFields:
    _id: str
    id: str
    instructions: str
    input: str = None
    output: str
    coins: int
    points: int
    difficulty: str


class ChallengeData(Model, ChallengeFields):
    BASE: str = "challenges"
    RANKS = {}
    ALL = 0

    def __init__(self, rank: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.__dict__.update(ChallengeData.RANKS[rank])

    @classmethod
    def read(cls, id: int | str):
        for rank in os.listdir(f"./data/{cls.BASE}"):
            for file_name in os.listdir(f"./data/{cls.BASE}/{rank}"):
                if f"{id}.json" == file_name:
                    return cls.by_rank_id(rank, id)

    @classmethod
    def by_rank_id(cls, rank: str, id: int | str):
        try:
            with open(f"./data/{cls.BASE}/{rank}/{id}.json", "r") as file:
                return cls(rank, id=int(id), **json.load(file))
        except FileNotFoundError:
            return None

    @classmethod
    def by_rank(cls, rank: str):
        files = os.listdir(f"./data/{cls.BASE}/{rank}")
        ids = [file[: file.index(".")] for file in files]
        return [cls.by_rank_id(rank, id) for id in ids]

amount = 0
for index, (rank, difficulty) in enumerate(
    [("apprentice", "easy"), ("knight", "normal"), ("wizard", "medium")], 1
):
    points = index * 25
    coins = index * 25 * len(os.listdir(f"./data/challenges/{rank}"))
    ChallengeData.ALL += len(os.listdir(f"./data/challenges/{rank}"))

    ChallengeData.RANKS[rank] = {
        "coins": 6.9 * index,
        "points": 25 * index,
        "difficulty": difficulty,
        "max": amount,
    }
    amount += points * len(os.listdir(f"./data/challenges/{rank}"))
