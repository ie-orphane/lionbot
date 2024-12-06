from discord.ext import commands
from constants import COLOR


class Cog(commands.Cog):
    color = COLOR

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
