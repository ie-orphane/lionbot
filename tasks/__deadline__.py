import discord
from discord.ext import tasks, commands
from models import ChannelData, FileData, UserData
from datetime import datetime, UTC, timedelta
from consts import COLOR, MESSAGE
from utils import Log


@tasks.loop(seconds=15)
async def deadline(bot: commands.Bot):
    for channel in ChannelData.read_all():
        now = datetime.now(UTC).replace(second=0, microsecond=0)
        if channel.time == now:
            Log.job("Dead", "starting...")
            deadchannel = bot.get_channel(channel.id)
            deadrole = deadchannel.guild.get_role(channel.role)
            await deadchannel.set_permissions(deadrole, send_messages=False)
            channel.remove()
            Log.job("Dead", f"{deadchannel} closed!")

    for file in FileData.read_all():
        now = datetime.now(UTC).replace(second=0, microsecond=0)
        if file.time == now:
            Log.job("File", "sending")
            filechannel = bot.get_channel(file.channel)
            await filechannel.send(file=discord.File(f"./assets/files/{file.id}"))
            file.remove()
            Log.job("File", f"{file.id} sended to {filechannel}!")

    for user in UserData.read_all():
        curent_challange = user.challenge
        if curent_challange:
            now = datetime.now(UTC).replace(second=0, microsecond=0)
            deadtime = datetime.fromisoformat(curent_challange.requested).replace(
                second=0, microsecond=0
            ) + timedelta(days=1)

            if now > deadtime:
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
                                f"{MESSAGE.failing}\n\nChallenge : **{curent_challange.name}"
                                f"**\nLanguage : {curent_challange.language}\nLevel : "
                                f"{curent_challange.level}\nResult : **DEAD**"
                            ),
                        )
                    )
                except Exception as e:
                    Log.error(
                        "Evaluation", f"Failed to send a message to {user.name} ({e})"
                    )

                Log.job("Evaluation", f"{curent_challange.name} is Dead!")
