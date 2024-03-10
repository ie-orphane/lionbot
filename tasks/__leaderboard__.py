import discord
from discord.ext import commands, tasks
from help import *

@tasks.loop(minutes=15)
async def leaderboard(bot: commands.Bot):
    print(
        f"\n{const.black(datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S'))} {const.yellow('Info')}     {const.magenta('Leaderboard')}  Updating leaderboard..."
    )

    data: dict = get_data()
    current_time = f"{datetime.now(UTC):%A  %d  %b    %I:%M  %p}"
    current_time = current_time.replace("AM", "am").replace("PM", "pm")
    current_week = get_week()
    params = {"start": current_week.readable_start, "end": current_week.readable_end}

    Time = datetime.now(UTC)
    users = []

    for user in data.values():
        if user.verified and user.student:
            print(f"{user.full_name:<20}", end=" ")
            fetch_time = datetime.now(UTC)

            user_summary = user.session.get(
                "users/current/summaries", params=params
            ).json()

            print(datetime.now(UTC) - fetch_time)

            languages = {}

            try:
                for day in user_summary["data"]:
                    for lang in day["languages"]:
                        if lang["name"] == "Other":
                            break

                        try:
                            languages[lang["name"]] += lang["total_seconds"]
                        except:
                            languages[lang["name"]] = lang["total_seconds"]
            except:
                print(user, user_summary)

            languages = [
                lang
                for lang, _ in sorted(
                    languages.items(), key=lambda x: x[1], reverse=True
                )
            ]
            if len(languages) > 4:
                languages = languages[:4]
            languages = ", ".join(languages)

            total_txt: str = user_summary["cumulative_total"]["text"]
            total_txt = total_txt.replace(" hrs", "h").replace(" mins", "min").replace(" secs", "s")

            users.append(
                [
                    user_summary["cumulative_total"]["seconds"],
                    {
                        "Coder": user.full_name,
                        "Total": total_txt,
                        "Languages": languages,
                    },
                ]
            )

    print(f"{str(datetime.now(UTC) - Time):>{14+1+20}}\n")
    users = sorted(users, key=lambda x: x[0], reverse=True)

    new_users = []
    for index, user_list in enumerate(users, start=1):
        user_list[1][""] = index
        new_users.append(user_list[1])
    users = new_users

    # top leaderboard image
    leaderboard_image(
        "first",
        "white",
        "black",
        "top_leaderboard",
        users,
        {
            "count": current_week.count,
            "start": current_week.human_readable_start,
            "end": current_week.human_readable_end,
        },
    )

    # bottom leaderboard image
    leaderboard_image(
        "last", "white", "black", "bottom_leaderboard", users, {"time": current_time}
    )


    leaderboard_channels: dict = open_file("data/data.json")["channels"]

    for channel_id, messages in leaderboard_channels.items():
        leaderboard_channel = bot.get_channel(int(channel_id))

        if leaderboard_channel:
            top_leaderboard = discord.File(
                "assets/top_leaderboard.png", filename="top_leaderboard.png"
            )
            bottom_leaderboard = discord.File(
                "assets/bottom_leaderboard.png", filename="bottom_leaderboard.png"
            )

            leaderboard_top: discord.Message = await leaderboard_channel.fetch_message(
                messages["top"]
            )
            leaderboard_bottom: discord.Message = (
                await leaderboard_channel.fetch_message(messages["bottom"])
            )

            await leaderboard_top.edit(attachments=[top_leaderboard])
            await leaderboard_bottom.edit(attachments=[bottom_leaderboard])
            print(
                f"{str(leaderboard_channel):<21} {leaderboard_channel.guild}"
            )

    print(
        f"\n{const.black(datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S'))} {const.blue('Info')}     {const.magenta('Leaderboard')}  Leaderboard updated!"
    )
