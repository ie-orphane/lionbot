from datetime import UTC, datetime, timedelta

import discord
from discord.ext import commands, tasks

from consts import COLOR, MESSAGE
from models import EvaluationData, UserData
from utils import Log


@tasks.loop(seconds=15)
async def dead(bot: commands.Bot):
    for user in UserData.read_all():
        curent_challange = user.challenge
        if curent_challange:
            now = datetime.now(UTC).replace(second=0, microsecond=0)
            deadtime = datetime.fromisoformat(curent_challange.requested).replace(
                second=0, microsecond=0
            ) + timedelta(days=1)

            if now > deadtime:
                EvaluationData(timestamp=str(now.timestamp()).replace(".", "_")).log(
                    f"Datetime: {now}",
                    f"User: {user.id}",
                    f"Challenge: {curent_challange.id}",
                    f"Language: {curent_challange.language}",
                    f"Attempt: {curent_challange.attempt}",
                    f"Result: DEAD",
                )
                user._challenge.update({"result": "DEAD"})

                user._challenges.append(user._challenge)
                user._challenge = None

                user.update()

                try:
                    discord_user = await bot.fetch_user(user.id)
                    await discord_user.send(
                        embed=discord.Embed(
                            color=COLOR.red,
                            description=(
                                f"{MESSAGE.failing}\n\n"
                                f"**`Challenge`**: **{curent_challange.name}**\n"
                                f"**`Language`**: {curent_challange.language}\n"
                                f"**`Level`**: {curent_challange.level}\n"
                                f"**`Result`**: **DEAD**"
                            ),
                        )
                    )
                except Exception as e:
                    Log.error(
                        "Evaluation", f"Failed to send a message to {user.name} ({e})"
                    )

                Log.job("Evaluation", f"{curent_challange.name} is Dead!")
