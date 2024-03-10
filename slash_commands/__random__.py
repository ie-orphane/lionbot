import discord, random
from discord.ext import commands
from models import UserData


class Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="random", description="pick random student(s)")
    @discord.app_commands.describe(count="how much? (all number supported)")
    async def profile_command(
        self,
        interaction: discord.Interaction,
        count: discord.app_commands.Range[int, 1, 22],
    ):
        await interaction.response.defer()

        users = UserData.read_all()
        random.shuffle(users)

        users_mention = "\n".join([f"<@{user.id}>" for user in users[:count]])
        await interaction.followup.send(users_mention)


async def setup(bot: commands.Bot):
    await bot.add_cog(Random(bot))
