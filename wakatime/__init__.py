import requests
from datetime import datetime, UTC


def get_week_summary(api_key: str, params: dict, name: str):
    print(f"{name:<20}", end=" ")
    fetch_time = datetime.now(UTC)

    headers = {"Authorization": f"Basic {api_key}", "Content-Type": "application/json"}
    url = "https://wakatime.com/api/v1/users/current/summaries"

    response = requests.get(url, params=params, headers=headers)

    if response.status_code != 200:
        print(f"Error {response.status_code} : {response.text}")
        return

    summary = response.json()
    languages = {}

    for day in summary["data"]:
        for lang in day["languages"]:
            languages.setdefault(lang["name"], 0)
            languages[lang["name"]] += lang["total_seconds"]

    languages = [
        lang for lang, _ in sorted(languages.items(), key=lambda x: x[1], reverse=True)
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

    print(datetime.now(UTC) - fetch_time)

    return (
        summary["cumulative_total"]["seconds"],
        {
            "Coder": name,
            "Total": "" if total_txt == "0s" else total_txt,
            "Languages": languages,
        },
    )
