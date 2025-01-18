import time
from utils import Log
from typing import Literal
from env import WAKATIME_API_URL
from . import __self__ as api


__all__ = ["WakatimeApi"]


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

            if (
                summary := await api.get(
                    url=f"{WAKATIME_API_URL}/users/current/summaries",
                    headers={
                        "Authorization": f"Basic {token}",
                        "Content-Type": "application/json",
                    },
                    name_message="Wakatime Api",
                    error_message=f"{name:<20}: {{response.status}} {{text}}",
                    **params,
                )
            ) is None:
                return None

            languages = {}

            for day in summary["data"]:
                for lang in day["languages"]:
                    languages.setdefault(lang["name"], 0)
                    languages[lang["name"]] += lang["total_seconds"]

            languages = [
                lang
                for lang, _ in sorted(
                    languages.items(), key=lambda x: x[1], reverse=True
                )
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

            Log.info("Wakatime Api", f"{name:<20}: {time.time() - start_time}")

            return (
                summary["cumulative_total"]["seconds"],
                {
                    "Coder": name,
                    "Total": "" if total_txt == "0s" else total_txt,
                    "Languages": languages,
                },
            )
        except Exception as e:
            Log.error("Wakatime Api", f"{type(e).__name__} {e}")
