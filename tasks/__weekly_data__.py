from discord.ext import tasks, commands
from datetime import datetime, UTC
from utils import get_files, Log, get_week, Week
from models import UserData, WeekData
from consts import GOLDEN_RATIO
from api import wakapi


THRESHOLD = 19_800
FACTOR = THRESHOLD / GOLDEN_RATIO


@tasks.loop(minutes=15)
async def weekly_data(bot: commands.Bot):
    try:
        weeks_file = get_files("./data/weeks")

        current_week: Week = get_week(week_argument="beforelast")
        week_count = current_week.count

        if datetime.now(UTC).weekday() == 0 and week_count not in weeks_file:
            Log.job("Data", "Collecting...")

            geeks = {
                user_summary.id: user_summary.total_seconds
                for user_summary in await wakapi.get_all_weekly_summary(
                    start=current_week.readable_start,
                    end=current_week.readable_end,
                )
                if not (user_summary is None)
            }

            # update users data
            for id, amount in geeks.items():
                user_data = UserData.read(id)
                if amount >= THRESHOLD:
                    user_data.add_coins(amount / FACTOR, "coding gain")
                    user_data.update()

            # update weeks data
            WeekData(
                id=current_week.count,
                start=current_week.readable_start,
                end=current_week.readable_end,
                geeks=dict(sorted(geeks.items(), key=lambda x: x[1], reverse=True)),
            ).update()

            Log.job("Data", "Collected!")
    except Exception as e:
        Log.error("Weekly Data", f"{type(e).__name__} {e}")
