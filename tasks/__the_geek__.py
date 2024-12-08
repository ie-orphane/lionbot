from utils import Log
from models import WeekData
from config import get_config
from constants import COLOR
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

    # get Geek of the week and black list roles
    for role in guild.roles:
        if role.name == "The Geek":
            geek_role = role
        if role.name == "Black List":
            black_list_role = role

    # if not found create new one
    if not geek_role:
        geek_role = await guild.create_role(name="The Geek", color=COLOR.yellow)
    if not black_list_role:
        black_list_role = await guild.create_role(
            name="Black List", color=COLOR.black
        )

    geek_id = None
    for id in last_week.geeks:
        black_list_member = [
            member for member in black_list_role.members if member.id == int(id)
        ]

        if black_list_member:
            try:
                await black_list_member[0].remove_roles(geek_role)
                await black_list_member[0].edit(
                    nick=black_list_member[0].display_name.replace(" 🏆", "")
                )
            except Exception as e:
                print(guild, e)

            continue

        geek_id = int(id)
        break

    for member in geek_role.members:
        if member.id == geek_id:
            return

    Log.job("TheGeek", "Updating")

    for geek_memeber in geek_role.members:
        try:
            await geek_memeber.remove_roles(geek_role)
            await geek_memeber.edit(nick=geek_memeber.display_name.replace(" 🏆", ""))
        except Exception as e:
            print(guild, e)

    for member in guild.members:
        if member.id == geek_id:
            try:
                await member.add_roles(geek_role)
                await member.edit(nick=member.display_name + " 🏆")
            except Exception as e:
                Log.error("TheGeek", f"Failed : {e}")
                return

    Log.job("TheGeek", "Updated!")
