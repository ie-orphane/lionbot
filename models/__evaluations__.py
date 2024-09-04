import json
from models.__schema__ import Document
from models import UserData, ChallengeData


class EvaluationData(Document):
    BASE: str = "evaluations"
    solution: str
    user: UserData
    challenge: ChallengeData

    def __to_dict__(self):
        self.__dict__.update(
            user=self.user.id,
            level=self.challenge.level,
            language=self.challenge.language,
        )
        if "challenge" in self.__dict__:
            self.__dict__.pop("challenge")
        return self.__dict__

    @classmethod
    def read_all(cls):
        with open(f"./data/{cls.BASE}.json", "r") as file:
            return [
                cls(
                    solution=x["solution"],
                    user=UserData.read(x["user"]),
                    challenge=ChallengeData.read(x["language"], x["level"]),
                )
                for x in json.load(file)
            ]
