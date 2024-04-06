import discord
from discord.ext import commands
from models import WeekData, UserData


class leaderbaord(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="leaderboard", description="Show previous leaderboards"
    )
    async def leaderboard_command(self, interaction: discord.Interaction):
        def formate_time(seconds: int):
            time = [
                (str(int(seconds / 3600)), "h"),
                (str(int((seconds % 3600) / 60)), "min"),
            ]
            time = filter(lambda x: x[0] != "0", time)
            time = map(lambda x: x[0] + x[1], time)
            return " ".join(time)

        def formate_name(name: str):
            name = name.strip().capitalize()
            return name

        await interaction.response.defer()

        week_select = discord.ui.Select(
            options=[
                discord.SelectOption(
                    label=f"{week_data:%l}     week #{week_data.id}", value=week_data.id
                )
                for week_data in sorted(
                    WeekData.read_all(), key=lambda x: x.id, reverse=True
                )
            ],
            placeholder="Select Week",
        )

        async def week_callback(_interaction: discord.Interaction):
            week = week_select.values[0]
            week_data = WeekData.read(week)

            table = (
                f"{' '*3}  |  {'Geek':^19}  |  {'Time':^9}  "
                f"\n{'-'*3}--|--{'-'*19}--|--{'-'*9}--"
            )

            for rank, geek_data in enumerate(week_data.geeks, 1):
                geek_name = UserData.read(geek_data.id).name
                table += f"\n{rank:>3}  |  {formate_name(geek_name):<19.19}  |  {formate_time(geek_data.amount):^9}"

            await interaction.followup.edit_message(
                message_id=message.id,
                content=None,
                embed=discord.Embed(
                    color=discord.Color.yellow(),
                    description=f"```week {week} {' '*3} {week_data:%l}\n\n{table}```",
                ),
                view=None,
            )

        week_select.callback = week_callback

        view = discord.ui.View(timeout=None)
        view.add_item(week_select)

        message = await interaction.followup.send(
            "## Select the deadline week:", view=view, ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(leaderbaord(bot))
