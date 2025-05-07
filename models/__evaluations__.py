import json

import env
from config import ChallengeConfig, get_challenge_by_id
from models.__schema__ import Document
from models.__users__ import UserData, solution


class EvaluationData(Document):
    BASE: str = "evaluations"
    solution: solution
    user: UserData
    challenge: ChallengeConfig
    timestamp: str

    def __to_dict__(self):
        self.__dict__.update(
            user=self.user.id,
            id=self.challenge.id,
            language=self.challenge.language,
        )
        self.__dict__.pop("challenge", None)
        return self.__dict__

    @classmethod
    def read_all(cls):
        with open(f"{env.BASE_DIR}/data/{cls.BASE}.json") as file:
            return [
                cls(
                    timestamp=x["timestamp"],
                    user=UserData.read(x["user"]),
                    challenge=get_challenge_by_id(x["language"], x["id"]),
                )
                for x in json.load(file)
            ]

    @property
    def solution(self):
        return solution(filename=f"{self.timestamp}.{self.challenge.extension}")

    def log(self, *content: str, sep="\n", end="\n"):
        with open(
            f"{env.BASE_DIR}/storage/evaluations/{self.timestamp}.ansi.log",
            "a",
        ) as f:
            f.write(sep.join(content) + end)
