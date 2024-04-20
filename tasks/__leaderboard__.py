import discord
import wakatime
from discord.ext import commands, tasks
from utils import clr, get_week, leaderboard_image, open_file
from datetime import datetime, UTC
from models import UserData


@tasks.loop(minutes=15)
async def leaderboard(bot: commands.Bot):
    print(
        f"{clr.black(datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S'))} {clr.yellow('Info')}     {clr.magenta('Leaderboard')}  Updating leaderboard..."
    )

    current_time = f"{datetime.now(UTC):%A  %d  %b    %I:%M  %p}"
    current_time = current_time.replace("AM", "am").replace("PM", "pm")
    current_week = get_week()
    params = {"start": current_week.readable_start, "end": current_week.readable_end}

    Time = datetime.now(UTC)

    users = [
        wakatime.get_week_summary(api_key=user.token, params=params, name=user.name)
        for user in UserData.read_all()
        if user and user.token
    ]

    print(f"{str(datetime.now(UTC) - Time):>{14+1+20}}\n")
    users_summary = sorted(users, key=lambda x: x[0], reverse=True)

    users = [
        {"": index, **user[1]} for index, user in enumerate(users_summary, start=1)
    ]

    # top and bottom global leaderboard image
    leaderboard_image(
        "top",
        "global",
        users[:11],
        count=current_week.count,
        start=current_week.human_readable_start,
        end=current_week.human_readable_end,
    )
    leaderboard_image("bottom", "global", users[11:], time=current_time)


    users = [
        {"": index, **user[1]}
        for index, user in enumerate(
            filter(lambda x: x[1]["Coder"] != "Forkani Mahdi", users_summary), start=1
        )
    ]


    # top and bottom codding II leaderboard image
    leaderboard_image(
        "top",
        "codingII",
        users[:11],
        count=current_week.count,
        start=current_week.human_readable_start,
        end=current_week.human_readable_end,
    )
    leaderboard_image("bottom", "codingII", users[11:], time=current_time)

    leaderboards_data: list[dict] = open_file("./data/leaderboards.json")

    for leaderboard_data in leaderboards_data:
        leaderboard_channel = bot.get_channel(leaderboard_data["channel"])
        for img, id in leaderboard_data["messages"].items():
            file = discord.File(
                f"./assets/images/{img}_leaderboard.png",
                filename=f"{img}_leaderboard.png",
            )
            message: discord.Message = await leaderboard_channel.fetch_message(id)
            await message.edit(content="", attachments=[file])

        print(f"{str(leaderboard_channel):<21} {leaderboard_channel.guild}")

    print(
        f"{clr.black(datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S'))} {clr.blue('Info')}     {clr.magenta('Leaderboard')}  Leaderboard updated!"
    )
