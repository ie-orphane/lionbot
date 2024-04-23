import discord
from discord.ext import tasks
import discord.ext
import discord.ext.commands
from models import ChannelData, FileData
from datetime import datetime, UTC
from utils import clr


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
            bot.log("Task", clr.yellow, "File", f"sending")
            filechannel = bot.get_channel(file.channel)
            await filechannel.send(file=discord.File(f"./assets/files/{file.name}"))
            file.remove()
            bot.log("Task", clr.green, "File", f"{file.name} sended to {filechannel}!")
