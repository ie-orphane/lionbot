from discord.ext import tasks, commands
from datetime import datetime, UTC
from utils import clr, color
from models import WeekData


@tasks.loop(minutes=5)
async def geek_of_the_week(bot: commands.Bot):

    last_week = WeekData.read_all()[-1]
    for guild in bot.guilds:
        geek_role = None
        black_list_role = None

        # get Geek of the week and black list roles
        for role in guild.roles:
            if role.name == "Geek of the week":
                geek_role = role
            if role.name == "Black List":
                black_list_role = role

        # if not found create new one
        if not geek_role:
            geek_role = await guild.create_role(
                name="Geek of the week", color=color.yellow
            )
        if not black_list_role:
            black_list_role = await guild.create_role(
                name="Black List", color=color.black
            )

        geek_id = None
        for geek in last_week.geeks:
            black_list_member = [
                member for member in black_list_role.members if member.id == geek.id
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

            geek_id = geek.id
            break

        if [geek_id] == [member.id for member in geek_role.members]:
            return

        print(
            f"\n{clr.black(f'{datetime.now(UTC):%Y-%m-%d %H:%M:%S}')} {clr.blue('Info')}     {clr.yellow('Geek Role')} {guild} Updating..."
        )

        for geek_memeber in geek_role.members:
            try:
                await geek_memeber.remove_roles(geek_role)
                await geek_memeber.edit(
                    nick=geek_memeber.display_name.replace(" 🏆", "")
                )
            except Exception as e:
                print(guild, e)

        for member in guild.members:
            if member.id == geek_id:
                try:
                    await member.add_roles(geek_role)
                    await member.edit(nick=member.display_name + " 🏆")
                except Exception as e:
                    print(guild, e)

        print(
            f"\n{clr.black(f'{datetime.now(UTC):%Y-%m-%d %H:%M:%S}')} {clr.blue('Info')}     {clr.yellow('Geek Role')} {guild} Updated!"
        )
