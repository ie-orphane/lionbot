from utils import Log
from models import WeekData
from config import get_config
from consts import COLOR
from discord.ext import tasks, commands


@tasks.loop(minutes=5)
async def the_geek(bot: commands.Bot):
    last_week = list(sorted(WeekData.read_all(), key=lambda x: x.id))[-1]

    if (guild_id := get_config("GUILD")) is None:
        Log.error("TheGeek", "guild id not found")
        return

    if (guild := bot.get_guild(guild_id)) is None:
        Log.error("TheGeek", "guild not found")
        return

    geek_role = None
    black_list_role = None

    for role in guild.roles:
        if role.name == "The Geek":
            geek_role = role
        if role.name == "Black List":
            black_list_role = role

    if not geek_role:
        geek_role = await guild.create_role(name="The Geek", color=COLOR.yellow)
    if not black_list_role:
        black_list_role = await guild.create_role(name="Black List", color=COLOR.black)

    the_geek = None
    try:
        the_geek_id = int(next(iter(last_week.geeks.keys())))
        for member in guild.members:
            if member.id == the_geek_id:
                the_geek = member
    except StopIteration:
        return

    if the_geek is None:
        return

    try:
        if the_geek in black_list_role.members:
            await the_geek.remove_roles(black_list_role)
            Log.info("TheGeek", "Removed from blacklist!")
    except Exception as e:
        Log.error("TheGeek", f"Failed : {e}")
        return

    for member in geek_role.members:
        if member.id != the_geek_id:
            try:
                await member.remove_roles(geek_role)
                await member.edit(
                    nick=member.display_name.replace(" 🏆", "")
                )
            except Exception as e:
                Log.error("TheGeek", f"Failed : {e}")

    for member in geek_role.members:
        if member.id == the_geek_id:
            return

    Log.job("TheGeek", "Updating...")

    try:
        await the_geek.add_roles(geek_role)
        await the_geek.edit(nick=the_geek.display_name + " 🏆")
    except Exception as e:
        Log.error("TheGeek", f"Failed : {e}")
        return

    Log.job("TheGeek", "Updated!")
