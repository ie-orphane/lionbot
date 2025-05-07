import os
import re
from datetime import UTC, datetime
from urllib.parse import urlparse

import requests

import env
from config import (
    ChallengeConfig,
    get_challenge_by_id,
    get_challenge_by_level,
    get_challenges,
)
from models.__schema__ import Collection, Model
from notations import CHALLENGE, SOCIAL


class Log(Model):
    name: str
    language: CHALLENGE.LANGUAGE
    id: int
    attempt: int
    trace: str
    result: CHALLENGE.RESULT
    cost: int


class filebase(Model):
    BASE: str
    filename: str

    def __init_subclass__(cls, BASE=None):
        if BASE is None:
            raise ValueError("BASE must be defined in the subclass")
        if not isinstance(BASE, str):
            raise TypeError("BASE must be a string")
        if not BASE:
            raise ValueError("BASE cannot be empty")
        cls.BASE = BASE

    @property
    def path(self):
        return f"{env.BASE_DIR}/storage/{self.BASE}/{self.filename}"


class solution(filebase, BASE="solutions"): ...


class UserChallenge(ChallengeConfig):
    attempt: int
    requested: datetime
    submited: datetime = None
    evaluated: datetime = None
    result: CHALLENGE.RESULT = None
    log: str = None
    timestamp: str = None

    def __init__(self, language: CHALLENGE.LANGUAGE, id: str, **kwargs) -> None:
        self.__dict__.update({**kwargs, **get_challenge_by_id(language, id).__dict__})

    @property
    def solution(self) -> solution:
        if self.timestamp is None:
            self.timestamp = str(datetime.now(UTC).timestamp()).replace(".", "_")
        return solution(filename=f"{self.timestamp}.{self.extension}")


class UserSocials:
    github: str = None
    portfolio: str = None
    linkedin: str = None

    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)

    def __iter__(self):
        return iter(self.__dict__.items())

    def exists(self, social: SOCIAL) -> bool:
        link = self.__dict__.get(social)
        return link is not None

    @staticmethod
    def isvalid(link: str) -> bool:
        tokens = urlparse(link)
        return all(
            getattr(tokens, qualifying_attr) for qualifying_attr in ("scheme", "netloc")
        )


class UserData(Collection):
    BASE = "users"
    id: int
    name: str
    coins: float
    token: str
    github: str
    portfolio: str
    training: str
    _challenges: list[dict]
    _challenge: dict | None = None
    _log: dict | None = None
    cooldowns: dict | None = None
    _socials: dict
    achievments: dict
    greylist: bool = False
    quests: list[str] = None

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

    @property
    def mention(self):
        return f"<@{self.id}>"

    def sub_coins(self, amount: int, reason: str):
        with open(
            os.path.join(os.path.abspath(env.BASE_DIR), "data", "transactions.csv"), "a"
        ) as f:
            print(
                f"{datetime.now(UTC)},{self.id},{self.coins},sub,{amount},{reason}",
                file=f,
            )
        self.coins -= amount
        self.update()
        return self.coins

    def add_coins(self, amount: int | float, reason: str):
        with open(
            os.path.join(os.path.abspath(env.BASE_DIR), "data", "transactions.csv"), "a"
        ) as f:
            print(
                f"{datetime.now(UTC)},{self.id},{self.coins},add,{amount},{reason}",
                file=f,
            )
        self.coins += amount
        self.update()
        return self.coins

    def request_challenge(self, language: CHALLENGE.LANGUAGE):
        all_challenges = get_challenges(language)
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

        challenge = get_challenge_by_level(language, level)

        self._challenge = {
            "id": challenge.id,
            "language": challenge.language,
            "attempt": attempt,
            "requested": str(datetime.now(UTC)),
        }

        if attempt > 7:
            self.sub_coins(challenge.coins * 0.07, "challenge cost")

        self.update()

        return challenge

    def add_social(self, social: SOCIAL, link: str):
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
            case "linkedin":
                if not re.match(
                    r"https:\/\/www\.linkedin\.com\/in\/[a-zA-Z0-9-]+", link
                ):
                    return None
        self._socials[social] = link
        self.update()
        return link

    def add_quest(self, language: str) -> bool:
        if not self.quests:
            self.quests = []
        if language in self.quests:
            return False
        self.quests.append(language)
        self.update()
        return True
