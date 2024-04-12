import discord, random
from discord.ext import commands
from models import UserData
from utils import open_file


class Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="random", description="pick random student(s)")
    @discord.app_commands.default_permissions(administrator=True)
    @discord.app_commands.guild_only()
    @discord.app_commands.describe(count="how much? (all number supported)", exclusive="pick non-repetitive student(s)")
    async def profile_command(
        self,
        interaction: discord.Interaction,
        count: discord.app_commands.Range[int, 1, 22] = 1,
        exclusive: bool = False,
    ):
        await interaction.response.defer()

        users = UserData.read_all()

        if exclusive:
            selected_users: list = open_file("data/selected_users.json")
            if len(selected_users) == 22:
                selected_users = []
            users: list = [user for user in users if user.id not in selected_users]

        random.shuffle(users)

        if exclusive:
            selected_users.extend([user.id for user in users[:count]])
            open_file("data/selected_users.json", selected_users)

        users_mention = "\n".join([f"<@{user.id}>" for user in users[:count]])
        await interaction.followup.send(users_mention)


async def setup(bot: commands.Bot):
    await bot.add_cog(Random(bot))
