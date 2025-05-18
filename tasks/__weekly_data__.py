import os
from datetime import UTC, datetime

from discord.ext import commands, tasks

import env
from api import wakapi
from models import WeekData
from utils import Log, Week, get_files, get_week


@tasks.loop(minutes=15)
async def weekly_data(bot: commands.Bot):
    try:
        weeks_file = get_files(
            os.path.join(os.path.abspath(env.BASE_DIR), "data", "weeks")
        )

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

            WeekData(
                id=current_week.count,
                start=current_week.readable_start,
                end=current_week.readable_end,
                geeks=dict(sorted(geeks.items(), key=lambda x: x[1], reverse=True)),
            ).update()

            Log.job("Data", "Collected!")
    except Exception as e:
        Log.error("Weekly Data", f"{type(e).__name__} {e}")
