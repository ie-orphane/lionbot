import discord
import time
from api import WakatimeApi
from discord.ext import commands, tasks
from utils import Log, get_week, leaderboard_image
from datetime import datetime, UTC
from models import UserData
from config import get_message, set_message, get_config


@tasks.loop(minutes=15)
async def leaderboard(bot: commands.Bot):
    try:
        Log.job("Leaderboard", "Updating...")

        current_time = f"{datetime.now(UTC):%A  %d  %b    %I:%M  %p}"
        current_time = current_time.replace("AM", "am").replace("PM", "pm")
        current_week = get_week()

        start_time = time.time()

        users_summary = []
        trainings: dict[str, list] = {}

        for user in UserData.read_all():
            if user and user.token:
                if user_summary := await WakatimeApi.get_weekly_summary(
                    user.token,
                    user.name,
                    start=current_week.readable_start,
                    end=current_week.readable_end,
                ):
                    users_summary.append(user_summary)
                    if user.training:
                        trainings.setdefault(user.training, [])
                        trainings[user.training].append(user.name)

        Log.info("Leaderboard", f"{' '*(20+1)}  {str(time.time() - start_time)}")

        users_summary.sort(key=lambda x: x[0], reverse=True)

        all_users = [
            {"": index, **user[1]}
            for index, user in enumerate(users_summary, start=1)
            if user[0] != 0
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

        for training, coders in trainings.items():
            users = [
                {"": index, **user[1]}
                for index, user in enumerate(
                    filter(lambda x: x[1]["Coder"] in coders, users_summary), start=1
                )
            ]

            leaderboard_image(
                "top",
                training,
                users[: len(users) // 2],
                count=current_week.count,
                start=current_week.human_readable_start,
                end=current_week.human_readable_end,
            )
            leaderboard_image(
                "bottom", training, users[len(users) // 2 :], time=current_time
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
