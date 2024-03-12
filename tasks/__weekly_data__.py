from datetime import datetime, UTC
from utils import open_file, get_files, clr
from discord.ext import tasks
from help import get_week, Week
from models import UserData, WeekData, LedgerData, GeekData


@tasks.loop(minutes=15)
async def weekly_data():
    weeks_file = get_files("data/weeks")

    current_week: Week = get_week(week_argument="beforelast")
    week_count = current_week.count

    if datetime.now(UTC).weekday() == 0 and week_count not in weeks_file:
        print(
            f"{clr.black(f'{datetime.now(UTC):%Y-%m-%d %H:%M:%S}')} {clr.blue('Info')}     {clr.yellow('Data')}  Updating..."
        )

        data: dict = open_file("data/data.pickle")

        params = {
            "start": current_week.readable_start,
            "end": current_week.readable_end,
        }

        geeks = []

        count = 1
        # get wakatime data
        for id, user in data.items():
            if user.verified and user.student:

                user_summary = user.session.get(
                    "users/current/summaries", params=params
                ).json()

                print(count, user.full_name)
                count += 1

                languages = {}

                try:
                    for day in user_summary["data"]:
                        for lang in day["languages"]:
                            try:
                                languages[lang["name"]] += lang["total_seconds"]
                            except KeyError:
                                languages[lang["name"]] = lang["total_seconds"]
                except:
                    print(user, user_summary)

                geeks.append(
                    GeekData(
                        id=id,
                        amount=user_summary["cumulative_total"]["seconds"],
                        languages={
                            lang: amount
                            for lang, amount in sorted(
                                languages.items(), key=lambda x: x[1], reverse=True
                            )
                        },
                    )
                )

        geeks.sort(key=lambda x: x.amount, reverse=True)

        # update users data
        for geek in geeks:
            user_data = UserData.read(geek.id)

            # deposit coins
            if geek.amount >= 18900:
                user_data.coins += geek.amount / 2022
                user_data.ledger.append(
                    LedgerData(
                        moment=str(datetime.now(UTC)),
                        type="deposit",
                        amount=geek.amount / 2022,
                    )
                )

            user_data.update()

        # update weeks data
        WeekData(
            id=current_week.count,
            start=current_week.readable_start,
            end=current_week.readable_end,
            geeks=geeks,
        ).update()

        print(
            f"{clr.black(f'{datetime.now(UTC):%Y-%m-%d %H:%M:%S}')} {clr.blue('Info')}     {clr.yellow('Data')}  updated!"
        )
