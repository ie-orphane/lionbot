from discord.ext import tasks, commands
from utils import clr, log, COLOR
from models import WeekData


@tasks.loop(minutes=5)
async def geek_of_the_week(bot: commands.Bot):
    discord_color = COLOR()
    last_week = list(sorted(WeekData.read_all(), key=lambda x: x.id))[-1]

    for guild in bot.guilds:
        if "LionsGeek" in guild.name:
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
                    name="Geek of the week", color=discord_color.yellow
                )
            if not black_list_role:
                black_list_role = await guild.create_role(
                    name="Black List", color=discord_color.black
                )

            geek_ids = []
            for training, coders in last_week.geeks.items():
                if training == "null":
                    continue

                for id in coders:
                    black_list_member = [
                        member
                        for member in black_list_role.members
                        if member.id == int(id)
                    ]

                    if black_list_member:
                        try:
                            await black_list_member[0].remove_roles(geek_role)
                            await black_list_member[0].edit(
                                nick=black_list_member[0].display_name.replace(
                                    " 🏆", ""
                                )
                            )
                        except Exception as e:
                            print(guild, e)

                        continue

                    geek_ids.append(int(id))
                    break

            identical = True
            for member_id in [member.id for member in geek_role.members]:
                if member_id not in geek_ids:
                    identical = False
                    break
            if identical:
                continue

            print(log("Task", clr.yellow, "Geek Role", "Updating"))

            for geek_memeber in geek_role.members:
                try:
                    await geek_memeber.remove_roles(geek_role)
                    await geek_memeber.edit(
                        nick=geek_memeber.display_name.replace(" 🏆", "")
                    )
                except Exception as e:
                    print(guild, e)

            for member in guild.members:
                if member.id in geek_ids:
                    try:
                        await member.add_roles(geek_role)
                        await member.edit(nick=member.display_name + " 🏆")
                    except Exception as e:
                        print(guild, e)

            print(log("Task", clr.green, "Geek Role", "Updated!"))
