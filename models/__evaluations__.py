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

    def __to_dict__(self):
        self.__dict__.update(
            user=self.user.id,
            id=self.challenge.id,
            language=self.challenge.language,
        )
        if "challenge" in self.__dict__:
            self.__dict__.pop("challenge")
        if "solution" in self.__dict__:
            self.__dict__["solution"] = self.solution.filename
        return self.__dict__

    @classmethod
    def read_all(cls):
        with open(f"{env.BASE_DIR}/data/{cls.BASE}.json") as file:
            return [
                cls(
                    solution=solution(filename=x["solution"]),
                    user=UserData.read(x["user"]),
                    challenge=get_challenge_by_id(x["language"], x["id"]),
                )
                for x in json.load(file)
            ]
