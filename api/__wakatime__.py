import time
from utils import Log
from env import WAKATIME_ENDPOINT
from . import __self__ as api


__all__ = ["WakatimeApi"]


class WakatimeApi:

    @classmethod
    async def get_all_time(cls, token: str, /):
        return await api.get(
            url=f"{WAKATIME_ENDPOINT}/users/current/stats/all_time",
            headers={
                "Authorization": f"Basic {token}",
                "Content-Type": "application/json",
            },
        )

    @classmethod
    async def get_weekly_summary(
        cls, token: str, name: str, /, **params
    ) -> tuple[int, dict] | None:
        try:
            start_time = time.time()

            if (
                summary := await api.get(
                    url=f"{WAKATIME_ENDPOINT}/v1/users/current/summaries",
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
