import discord
from api import wakapi
from discord.ext import commands, tasks
from utils import Log, get_week, leaderboard_image
from datetime import datetime, UTC
from config import get_message, set_message, get_config


@tasks.loop(minutes=15)
async def leaderboard(bot: commands.Bot):
    try:
        Log.job("Leaderboard", "Updating...")

        current_time = f"{datetime.now(UTC):%A  %d  %b    %I:%M  %p}"
        current_time = current_time.replace("AM", "am").replace("PM", "pm")
        current_week = get_week()

        users_summary = await wakapi.get_all_weekly_summary(
            start=current_week.readable_start,
            end=current_week.readable_end,
        )

        trainings_summary = {}
        for user_summary in users_summary:
            if user_summary.training is None:
                continue
            trainings_summary.setdefault(user_summary.training, [])
            trainings_summary[user_summary.training].append(
                {
                    "": len(trainings_summary[user_summary.training]) + 1,
                    **user_summary.data,
                }
            )

        all_users = [
            {"": index, **user_summary.data}
            for index, user_summary in enumerate(users_summary, start=1)
            if user_summary.total_seconds != 0
        ]

        if len(all_users) > 0:
            leaderboard_image(
                "top",
                "global",
                all_users[: len(all_users) // 3],
                count=current_week.count,
                start=current_week.human_readable_start,
                end=current_week.human_readable_end,
            )
            leaderboard_image(
                "middle",
                "global",
                all_users[len(all_users) // 3 : 2 * len(all_users) // 3],
            )
            leaderboard_image(
                "bottom",
                "global",
                all_users[2 * len(all_users) // 3 :],
                time=current_time,
            )

        for training, coders in trainings_summary.items():
            leaderboard_image(
                "top",
                training,
                coders[: len(coders) // 2],
                count=current_week.count,
                start=current_week.human_readable_start,
                end=current_week.human_readable_end,
            )
            leaderboard_image(
                "bottom", training, coders[len(coders) // 2 :], time=current_time
            )

        message: discord.Message
        message_id: int

        for leaderboard_data in get_config("ALL", "leaderboard"):
            leaderboard_channel = bot.get_channel(leaderboard_data["channel"])
            if leaderboard_channel is None:
                continue
            for position in leaderboard_data["messages"]:
                file = discord.File(
                    f"./assets/images/{leaderboard_data['alias']}_{position}_leaderboard.png",
                    filename=f"{position}_leaderboard.png",
                )
                if (
                    message_id := get_message(
                        "LEADERBOARD", f"{leaderboard_data['alias']}/{position}"
                    )
                ) is not None:
                    try:
                        message = await leaderboard_channel.fetch_message(message_id)
                        await message.edit(content="", attachments=[file])
                        continue
                    except discord.NotFound:
                        pass

                message = await leaderboard_channel.send(content="", file=file)
                set_message(
                    "LEADERBOARD",
                    f"{leaderboard_data['alias']}/{position}",
                    message.id,
                )

            Log.info(
                "Leaderboard",
                f"{str(leaderboard_channel):<21} {leaderboard_channel.guild}",
            )

        Log.job("Leaderboard", "updated!")

    except Exception as e:
        Log.error("Leaderboard", f"{type(e).__name__} {e}")
