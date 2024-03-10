import discord
from discord.ext import commands
from data.models import WeekData, UserData


class leaderbaord(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="leaderboard", description="Show previous leaderboards"
    )
    @discord.app_commands.describe(week="Choose a week")
    @discord.app_commands.choices(
        week=[
            discord.app_commands.Choice(
                name=f"{week_data:%l}     week #{week_data.id}", value=week_data.id
            )
            for week_data in WeekData.read_all()
        ]
    )
    async def leaderboard_command(self, interaction: discord.Interaction, week: int):
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

        week_data = WeekData.read(week)

        table = (
            f"{' '*3}  |  {'Geek':^19}  |  {'Time':^9}  "
            f"\n{'-'*3}--|--{'-'*19}--|--{'-'*9}--"
        )

        for rank, geek_data in enumerate(week_data.geeks, 1):
            geek_name = UserData.read(geek_data.id).name
            table += f"\n{rank:>3}  |  {formate_name(geek_name):<19.19}  |  {formate_time(geek_data.amount):^9}"

        leaderbaordEmbed = discord.Embed(
            color=discord.Color.yellow(),
            description=f"```week {week} {' '*3} {week_data:%l}\n\n{table}```",
        )
        await interaction.followup.send(embed=leaderbaordEmbed)


async def setup(bot: commands.Bot):
    await bot.add_cog(leaderbaord(bot))
