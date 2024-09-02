from models.__schema__ import Collection, Relation, Model
from models.__challenges__ import ChallengeData, ChallengeFields
from datetime import datetime, UTC
from utils import Language, Result


class Log(Model):
    name: str
    langauge: Language
    level: int
    attempt: int
    trace: str
    result: Result
    cost: int


class UserChallenge(Relation, ChallengeData, ChallengeFields):
    MODEL = ChallengeData
    attempt: int
    requested: datetime
    submited: datetime = None
    evaluated: datetime = None
    result: Result = None
    log: str = None
    _solution: str = None

    def __init__(self, langauge: Language, level: int, **kwargs) -> None:
        self.__dict__.update({**kwargs, **self.MODEL.read(langauge, level).__dict__})

    @property
    def solution(self):
        return (
            self._solution
            or f"assets/solutions/{self.language}/{int(datetime.now(UTC).timestamp())}.{self.extension}"
        )


class UserData(Collection):
    BASE = "users"
    id: int
    name: str
    coins: int
    token: str
    github: str
    portfolio: str
    training: str
    graduated: bool
    _challenges: list[dict]
    _challenge: dict | None
    _log: dict | None

    @property
    def challenge(self):
        if self._challenge:
            return UserChallenge(**self._challenge)
        return None

    @property
    def log(self):
        if self._log:
            return Log(**self._log)
        return None

    @property
    def challenges(self):
        return [UserChallenge(**challenge_data) for challenge_data in self._challenges]

    def sub_coins(self, amount: int, reason: str):
        with open("data/logs.csv", "a") as f:
            print(
                f"{datetime.now(UTC)},{self.id},{self.coins},sub,{amount},{reason}",
                file=f,
            )
        self.coins -= amount
        self.update()
        return self.coins

    def add_coins(self, amount: int, reason: str):
        with open("data/logs.csv", "a") as f:
            print(
                f"{datetime.now(UTC)},{self.id},{self.coins},add,{amount},{reason}",
                file=f,
            )
        self.coins += amount
        self.update()
        return self.coins

    def request_challenge(self, langauge: Language):
        all_challenges = ChallengeData.read_all(langauge)
        user_challenges = self.challenges

        level = 0
        attempt = 1
        for user_challenge in user_challenges:
            if user_challenge.language == langauge and user_challenge.level == level:
                if user_challenge.result == "OK":
                    level += 1
                    attempt = 1
                else:
                    attempt += 1

        if level >= len(all_challenges):
            return None

        challenge = ChallengeData.read(langauge, level)

        self._challenge = {
            "langauge": langauge,
            "level": level,
            "attempt": attempt,
            "requested": str(datetime.now(UTC)),
        }

        if attempt > 7:
            self.sub_coins(18.561, "challenge cost")

        self.update()

        return challenge
