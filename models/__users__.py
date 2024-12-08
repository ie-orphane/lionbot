import re
import requests
from urllib.parse import urlparse
from models.__schema__ import Collection, Relation, Model
from models.__challenges__ import ChallengeData, ChallengeFields
from datetime import datetime, UTC
from utils import Language, Result, Social


class Log(Model):
    name: str
    language: Language
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

    def __init__(self, language: Language, level: int, **kwargs) -> None:
        self.__dict__.update({**kwargs, **self.MODEL.read(language, level).__dict__})

    @property
    def solution(self):
        return (
            self._solution
            or f"assets/solutions/{self.language}/{int(datetime.now(UTC).timestamp())}.{self.extension}"
        )


class UserSocials:
    github: str = None
    portfolio: str = None

    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)

    def __iter__(self):
        return iter(self.__dict__.items())

    def exists(self, social: Social) -> bool:
        link = self.__dict__.get(social)
        return link is not None

    @staticmethod
    def isvalid(link: str) -> bool:
        tokens = urlparse(link)
        return all(
            getattr(tokens, qualifying_attr) for qualifying_attr in ("scheme", "netloc")
        )

    def extract_username_from_url(url):
        # Use regex to extract the username from the GitHub URL
        match = re.search(r"github\.com/([^/]+)", url)
        if match:
            return match.group(1)
        else:
            print("Invalid GitHub URL")
            return None


class UserData(Collection):
    BASE = "users"
    id: int
    name: str
    coins: float
    token: str
    github: str
    portfolio: str
    training: str
    graduated: bool
    _challenges: list[dict]
    _challenge: dict | None
    _log: dict | None
    _socials: dict
    achievments: dict

    @property
    def socials(self):
        return UserSocials(**self._socials)

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

    def request_challenge(self, language: Language):
        all_challenges = ChallengeData.read_all(language)
        user_challenges = self.challenges

        all_user_challenges: dict[tuple[int, str], list[UserChallenge]] = {}

        for challenge in user_challenges:
            if challenge.language == language:
                all_user_challenges.setdefault((challenge.level, challenge.name), [])
                all_user_challenges[(challenge.level, challenge.name)].append(challenge)

        all_user_challenges = dict(
            sorted(all_user_challenges.items(), key=lambda x: x[0][0])
        )

        level = 0
        attempt = 1
        for challenges in all_user_challenges.values():
            challenges.sort(key=lambda x: x.attempt)
            for challenge in challenges:
                if level == challenge.level:
                    if challenge.result == "OK":
                        level += 1
                        attempt = 1
                    else:
                        attempt += 1

        if level >= len(all_challenges):
            return None

        challenge = ChallengeData.read(language, level)

        self._challenge = {
            "language": language,
            "level": level,
            "attempt": attempt,
            "requested": str(datetime.now(UTC)),
        }

        if attempt > 7:
            self.sub_coins(challenge.coins * 0.07, "challenge cost")

        self.update()

        return challenge

    def add_social(self, social: Social, link: str):
        is_valid_link = UserSocials.isvalid(link)

        match social:
            case "github":
                url = "https://api.github.com/users/"
                if is_valid_link:
                    if match := re.search(r"github\.com/([^/]+)", link):
                        url += match.group(1)
                    else:
                        return None
                else:
                    url += link
                response = requests.get(url)
                if not response.ok:
                    return None
                if not (link := response.json().get("html_url")):
                    return None
            case "portfolio":
                if not is_valid_link:
                    return None
        self._socials[social] = link
        self.update()
        return link
