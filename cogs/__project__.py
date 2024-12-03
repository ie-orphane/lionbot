import discord
from cogs import Cog, COLOR
from models import ProjectData, UserData
from typing import Literal
from datetime import datetime, UTC, timedelta
from discord.ext import commands


class Send(Cog):
    @discord.app_commands.guild_only()
    @discord.app_commands.command(description="send a project")
    @discord.app_commands.describe(id="the project's ID")
    async def send_project(self, interaction: discord.Interaction, id: str, link: str):
        await interaction.response.defer()

        user = UserData.read(interaction.user.id)

        if user is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=(
                        f"✋ {interaction.user.mention}, "
                        "\nyou need to register before using the `/send_project` command."
                        "\nTo register, use the `/register` command"
                    ),
                )
            )
            return

        project = ProjectData.read(id)

        if project is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=(
                        f"❌ The provided project Id **`{id}`** seems to be invalid."
                        "\nPlease ensure you're using the correct one."
                    ),
                )
            )
            return

        deadtime = datetime.fromisoformat(project.deadtime)

        if datetime.now(UTC) > deadtime:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=(
                        f"**Uh oh!** The deadline for the project {project.name} has passed. ⏰"
                        f"\nRemember, the deadline was <t:{int(deadtime.timestamp())}:F>."
                    ),
                )
            )
            return

        project.add_link(interaction.user.id, link)

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                description=(
                    "✅ Project link successfully sent!"
                    f"\n(Id: **`{id}`**)"
                    f"\n[Link preview of the project]({link})"
                ),
            )
        )


@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
class Project(commands.GroupCog, name="project"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.color = COLOR

    @discord.app_commands.command(description="list all projects")
    async def all(self, interaction: discord.Interaction):
        await interaction.response.defer()

        projects = ProjectData.read_all()
        max_length = max(4, *map(lambda x: len(x.name), projects))

        content = [
            f"|                  id                  | {'name':^{max_length}} | links | {'DeadTime':^16} |",
            f"| :----------------------------------: | :{'-'*(max_length-2)}: | :---: | :{'-'*14}: |",
        ] + [
            f"| {project.id} | {project.name:^{max_length}} | {len(project.links):^5} | {datetime.fromisoformat(project.deadtime):%Y/%m/%d %H:%M} |"
            for project in projects
        ]

        await interaction.followup.send(f"```md\n{'\n'.join(content)}```")

    @discord.app_commands.command(description="get the links of a project")
    @discord.app_commands.describe(id="the project's ID")
    async def links(self, interaction: discord.Interaction, id: str):
        await interaction.response.defer()

        project = ProjectData.read(id)

        if project is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=(
                        f"❌ The provided project Id **`{id}`** seems to be invalid."
                        "\nPlease ensure you're using the correct one."
                    ),
                )
            )
            return

        project = ProjectData.read(id)

        content = project.name.lower().strip().replace(" ", "_")

        for user_id, link in project.links.items():
            content += (
                f"\n{UserData.read(user_id).name.lower().replace(" ", "_")}={link}"
            )

        await interaction.followup.send(f"```bash\n{content}```")

    @discord.app_commands.command(description="Get a new project id")
    @discord.app_commands.describe(
        name="the project's name",
        day="Enter dead day",
        hours="Enter dead hour in UTC timezone",
        minutes="Enter dead minutes in UTC timezone",
    )
    async def new(
        self,
        interaction: discord.Interaction,
        name: str,
        day: Literal[
            "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
        ],
        hours: discord.app_commands.Range[int, 0, 23],
        minutes: discord.app_commands.Range[int, 0, 59] = 0,
    ):
        await interaction.response.defer()

        days = {
            (datetime.now(UTC) + timedelta(days=day))
            .__format__("%A"): (datetime.now(UTC) + timedelta(days=day))
            .date()
            for day in range(7)
        }

        deadtime = datetime.fromisoformat(
            f"{days[day]} {hours:0>2}:{minutes:0>2}:00+00:00"
        )

        project_id = ProjectData.new(name, str(deadtime))

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                title=f"{name} initialsed!",
                description=f"Project Id :\n```\n{project_id}\n```\nDead Time : <t:{int(deadtime.timestamp())}:F>",
            )
        )


async def setup(bot):
    await bot.add_cog(Send(bot))
    await bot.add_cog(Project(bot))
