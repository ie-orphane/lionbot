import discord
from discord.ext import tasks
import discord.ext
import discord.ext.commands
from models import ChannelData, FileData, UserData
from datetime import datetime, UTC, timedelta
from utils import clr, COLOR, MESSAGE


@tasks.loop(seconds=15)
async def deadline(bot):
    for channel in ChannelData.read_all():
        now = datetime.now(UTC).replace(second=0, microsecond=0)
        if channel.time == now:
            bot.log("Task", clr.yellow, "Dead", "starting...")
            deadchannel = bot.get_channel(channel.id)
            deadrole = deadchannel.guild.get_role(channel.role)
            await deadchannel.set_permissions(deadrole, send_messages=False)
            channel.remove()
            bot.log("Task", clr.green, "Dead", "closed!")

    for file in FileData.read_all():
        now = datetime.now(UTC).replace(second=0, microsecond=0)
        if file.time == now:
            bot.log("Task", clr.yellow, "File", "sending")
            filechannel = bot.get_channel(file.channel)
            await filechannel.send(file=discord.File(f"./assets/files/{file.id}"))
            file.remove()
            bot.log("Task", clr.green, "File", f"{file.id} sended to {filechannel}!")

    for user in UserData.read_all():
        cuurent_challange = user.challenge
        if cuurent_challange:
            now = datetime.now(UTC).replace(second=0, microsecond=0)
            deadtime = datetime.fromisoformat(cuurent_challange.requested).replace(
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
                                f"{MESSAGE.failing}\n\nChallenge : **{cuurent_challange.name}"
                                f"**\nLanguage : {cuurent_challange.language}\nLevel : "
                                f"{cuurent_challange.level}\nResult : **DEAD**"
                            ),
                        )
                    )
                except Exception as e:
                    print(f"Failed to send a message to {user.name}\nError: {e}")

                bot.log(
                    "Task",
                    clr.green,
                    "Evaluation",
                    f"{cuurent_challange.name} is Dead!",
                )
