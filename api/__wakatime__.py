import time
from utils import Log
from typing import Literal
from env import WAKATIME_API_URL
from . import __self__ as api
from constants import BUFFER_SLEEP_SECONDS
from models import UserData
import aiohttp
import asyncio


class WakaData:
    id: int
    name: str
    training: str | None
    total_seconds: float
    languages: str
    total_time: str

    def __init__(self, user: UserData):
        self.id = user.id
        self.name = user.name
        self.training = user.training

    @property
    def data(self):
        return {
            "Coder": self.name,
            "Total": "" if self.total_time == "0s" else self.total_time,
            "Languages": "" if self.total_time == "0s" else self.languages,
        }


class WakatimeApi:

    @staticmethod
    async def __get(
        *, token: str, endpoint: str = "users/current", action: str = "", **params
    ):
        return await api.get(
            url=f"{WAKATIME_API_URL}/{'/'.join([path for path in f'{endpoint}/{action}'.split("/") if path])}",
            headers={
                "Authorization": f"Basic {token}",
                "Content-Type": "application/json",
            },
            **params,
        )

    @staticmethod
    def __get_weekly_summary(user: UserData, summary: dict) -> WakaData | None:
        if summary is None:
            return None

        wakadata = WakaData(user)

        languages = {}

        for day in summary["data"]:
            for lang in day["languages"]:
                languages.setdefault(lang["name"], 0)
                languages[lang["name"]] += lang["total_seconds"]

        languages = [
            lang
            for lang, _ in sorted(languages.items(), key=lambda x: x[1], reverse=True)
        ]
        if len(languages) > 4:
            languages = languages[:4]
        wakadata.languages = ", ".join(languages)

        wakadata.total_time = (
            summary["cumulative_total"]["text"]
            .replace(" hrs", "h")
            .replace(" mins", "min")
            .replace(" secs", "s")
        )

        wakadata.total_seconds = summary["cumulative_total"]["seconds"]

        return wakadata

    @staticmethod
    def __format_weekly_summary(name: str, summary: dict) -> tuple[float, dict] | None:
        if summary is None:
            return None

        languages = {}

        for day in summary["data"]:
            for lang in day["languages"]:
                languages.setdefault(lang["name"], 0)
                languages[lang["name"]] += lang["total_seconds"]

        languages = [
            lang
            for lang, _ in sorted(languages.items(), key=lambda x: x[1], reverse=True)
        ]
        if len(languages) > 4:
            languages = languages[:4]
        languages = ", ".join(languages)

        total_txt: str = (
            summary["cumulative_total"]["text"]
            .replace(" hrs", "h")
            .replace(" mins", "min")
            .replace(" secs", "s")
        )

        return (
            summary["cumulative_total"]["seconds"],
            {
                "Coder": name,
                "Total": "" if total_txt == "0s" else total_txt,
                "Languages": "" if total_txt == "0s" else languages,
            },
        )

    @classmethod
    async def get_current(cls, token: str, /):
        return await cls.__get(token=token)

    @classmethod
    async def get_stats(
        cls,
        token: str,
        duration: Literal["last_7_days", "last_30_days", "last_year", "all_time"],
        /,
    ):
        return await cls.__get(token=token, action=f"stats/{duration}")

    @classmethod
    async def get_all_time(cls, token: str, /):
        return await cls.get_stats(token, "all_time")

    @classmethod
    async def get_summary(cls, token: str, /, **params):
        return await cls.__get(token=token, action="summaries", **params)

    @classmethod
    async def get_weekly_summary(
        cls, token: str, name: str, /, **params
    ) -> tuple[int, dict] | None:
        try:
            start_time = time.time()
            summary = await api.get(
                url=f"{WAKATIME_API_URL}/users/current/summaries",
                headers={
                    "Authorization": f"Basic {token}",
                    "Content-Type": "application/json",
                },
                name_message="Wakatime Api",
                error_message=f"{name:<20}: {{response.status}} {{text}}",
                **params,
            )

            Log.info("Wakatime Api", f"{name:<20}: {time.time() - start_time}")

            return cls.__format_weekly_summary(name, summary)

        except Exception as e:
            Log.error("Wakatime Api", f"{type(e).__name__} {e}")

    @classmethod
    async def get_all_weekly_summary(cls, **params: dict) -> list[WakaData]:
        first_time = time.time()
        users = UserData.read_all()
        users_summary = []
        count = 0
        sleeped = 0

        while True:
            async with aiohttp.ClientSession() as session:

                for user in users.copy():
                    if user is None or user.token is None:
                        users.remove(user)
                        continue

                    start_time = time.time()

                    async with session.get(
                        f"{WAKATIME_API_URL}/users/current/summaries",
                        headers={
                            "Authorization": f"Basic {user.token}",
                            "Content-Type": "application/json",
                        },
                        params=params,
                    ) as response:

                        if response.status == 429:
                            Log.error("WAKATIME", "429 - Too Many Requests")
                            break

                        if response.status == 401:
                            user.token = None
                            user.update()

                        users.remove(user)
                        count += 1

                        if response.status == 200:
                            Log.info(
                                "WAKATIME",
                                f"{count:>2} {user.name:<21}: {time.time() - start_time:.3f}",
                            )
                            if not (
                                (
                                    user_summary := cls.__get_weekly_summary(
                                        user, await response.json()
                                    )
                                )
                                is None
                            ):
                                users_summary.append(user_summary)
                            continue

                        Log.error(
                            "WAKATIME", f"{response.status} - {await response.text()}"
                        )

            if len(users) == 0:
                break

            Log.warning(
                "WAKATIME",
                f"Buffer sleeping ({time.time() - first_time - sleeped:.2f})",
            )
            sleeped += BUFFER_SLEEP_SECONDS
            await asyncio.sleep(BUFFER_SLEEP_SECONDS)

        print(
            f"{" " * 64}{time.time() - first_time:.2f} ({time.time() - first_time - sleeped:.2f})"
        )
        users_summary.sort(key=lambda x: x.total_seconds, reverse=True)
        return users_summary
