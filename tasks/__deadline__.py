import discord
from discord.ext import tasks, commands
from models import DeadData, FileData
from datetime import datetime, UTC
from utils import clr


@tasks.loop(seconds=15)
async def dead_channel(bot: commands.Bot):
    for dead in DeadData.read_all():
        now = datetime.now(UTC).replace(second=0, microsecond=0)
        if dead.time == now:
            deadchannel = bot.get_channel(dead.channel)
            deadrole = deadchannel.guild.get_role(dead.role)
            await deadchannel.set_permissions(deadrole, send_messages=False)
            dead.remove()
            print(
                f"{clr.black(now.strftime('%Y-%m-%d %H:%M:%S'))} {clr.blue('Info')}     {clr.magenta('Dead')}  {deadchannel} closed!"
            )

    for file in FileData.read_all():
        now = datetime.now(UTC).replace(second=0, microsecond=0)
        if file.time == now:
            filechannel = bot.get_channel(file.channel)
            await filechannel.send(file=discord.File(f"assets/files/{file.name}"))
            file.remove()
            print(
                f"{clr.black(now.strftime('%Y-%m-%d %H:%M:%S'))} {clr.blue('Info')}     {clr.magenta('File')}  {file.name} sended to {filechannel}!"
            )
