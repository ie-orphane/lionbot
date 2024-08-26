from discord.ext import tasks
from datetime import datetime, UTC
from utils import get_files, clr, get_week, Week, log
from models import UserData, WeekData
from wakatime import get_week_summary


@tasks.loop(minutes=15)
async def weekly_data():
    weeks_file = get_files("./data/weeks")

    current_week: Week = get_week(week_argument="beforelast")
    week_count = current_week.count

    if datetime.now(UTC).weekday() == 0 and week_count not in weeks_file:
        print(log("Task", clr.yellow, "Data", "Collecting..."))

        geeks = {}
        for i, user in enumerate(UserData.read_all()):
            if user.token:
                print(f"[{i:>2}]", end=" ")
                user_summary = get_week_summary(
                    api_key=user.token,
                    params={
                        "start": current_week.readable_start,
                        "end": current_week.readable_end,
                    },
                    name=user.name,
                )

                if user_summary:
                    geeks[user.id] = user_summary[0]

        # update users data
        for id, amount in geeks.items():
            user_data = UserData.read(id)
            if amount >= 18900:
                user_data.coins += amount / 2022
                user_data.update()

        # update weeks data
        WeekData(
            id=current_week.count,
            start=current_week.readable_start,
            end=current_week.readable_end,
            geeks=dict(sorted(geeks.items(), key=lambda x: x[1], reverse=True)),
        ).update()

        print(log("Task", clr.green, "Data", "Collected!"))
