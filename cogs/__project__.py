import discord
from cogs import GroupCog
from models import ProjectData, UserData
from typing import Literal
from datetime import datetime, UTC, timedelta


@discord.app_commands.guild_only()
class Project(GroupCog, name="project"):
    @discord.app_commands.command(description="Submit a project for review.")
    @discord.app_commands.describe(id="The project's ID.", link="The project's link.")
    async def submit(self, interaction: discord.Interaction, id: str, link: str):
        await interaction.response.defer()

        if (await self.bot.user_is_unkown(interaction)) is None:
            return

        if (project := ProjectData.read(id)) is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=(
                        f"❌ {interaction.user.id}, \n"
                        f"the provided project Id **`{id}`** seems to be invalid."
                        "\nPlease ensure you're using the correct one."
                    ),
                )
            )
            return

        if str(interaction.user.id) in project.links:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=(
                        f"✋ {interaction.user.mention}, "
                        "\nyou already submitted the project link!"
                        "\nYou can use `/edit_project` command to edit the link."
                    ),
                )
            )
            return

        deadtime = datetime.fromisoformat(project.deadtime)
        now = datetime.now(UTC)

        project.add_link(
            user_id=interaction.user.id, link=link, now=now, dead=now > deadtime
        )

        if now > deadtime:
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

    @discord.app_commands.command(description="Edit a project's link.")
    @discord.app_commands.describe(id="The project's ID.", link="The project's link.")
    async def edit(self, interaction: discord.Interaction, id: str, link: str):
        await interaction.response.defer()

        if (await self.bot.user_is_unkown(interaction)) is None:
            return

        if (project := ProjectData.read(id)) is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=(
                        f"❌ {interaction.user.id}, \n"
                        f"the provided project Id **`{id}`** seems to be invalid."
                        "\nPlease ensure you're using the correct one."
                    ),
                )
            )
            return

        if str(interaction.user.id) not in project.links:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=(
                        f"✋ {interaction.user.mention}, "
                        "\nyou need to submit the project before using the `/edit_project` command."
                        "\nUse the `/send_project` command instaed"
                    ),
                )
            )
            return

        deadtime = datetime.fromisoformat(project.deadtime)
        now = datetime.now(UTC)

        if now > deadtime:
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

        project.add_link(user_id=interaction.user.id, link=link, now=now, dead=False)

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                description=(
                    "✅ Project link successfully updated!"
                    f"\n(Id: **`{id}`**)"
                    f"\n[Link preview of the project]({link})"
                ),
            )
        )


@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
class _Project(GroupCog, name="__project"):
    @discord.app_commands.command(description="List all the projects.")
    async def all(self, interaction: discord.Interaction):
        await interaction.response.defer()

        projects = ProjectData.read_all()
        max_length = max(4, *map(lambda x: len(x.name), projects))

        content = [
            f"|                  id                  | {'name':^{max_length}} | links | {'deadtime':^16} |",
            f"| :----------------------------------: | :{'-'*(max_length-2)}: | :---: | :{'-'*14}: |",
        ] + [
            f"| {project.id} | {project.name:^{max_length}} | {len(project.links):^5} | {datetime.fromisoformat(project.deadtime):%Y/%m/%d %H:%M} |"
            for project in projects
        ]

        await interaction.followup.send(f"```md\n{'\n'.join(content)}```")

    @discord.app_commands.command(description="Get the links of a project.")
    @discord.app_commands.describe(id="The project's ID.")
    async def links(self, interaction: discord.Interaction, id: str):
        await interaction.response.defer()

        if (project := ProjectData.read(id)) is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=(
                        f"❌ {interaction.user.id}, \n"
                        f"the provided project Id **`{id}`** seems to be invalid."
                        "\nPlease ensure you're using the correct one."
                    ),
                )
            )
            return

        project = ProjectData.read(id)

        content = project.name.lower().strip().replace(" ", "_")

        for user_id, link in project.links.items():
            content += f"\n{UserData.read(user_id).name.lower().replace(" ", "_")}={link['link']}"

        await interaction.followup.send(f"```bash\n{content}```")

    @discord.app_commands.command(description="Create a new project.")
    @discord.app_commands.describe(
        name="The project's name",
        day="The project's dead day.",
        hours="The project's dead hour in UTC timezone.",
        minutes="The project's dead minutes.",
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
    await bot.add_cog(_Project(bot))
    await bot.add_cog(Project(bot))
