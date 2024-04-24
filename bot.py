import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from tasks import leaderboard, weekly_data, geek_of_the_week, deadline
from utils import clr
from typing import Literal
from datetime import datetime, UTC


class Bot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix="-", intents=discord.Intents.all())
        self.coin = "<:lioncoin:1219417317419651173>"

    def log(self, type: Literal["Info", "Error", "Task"], func, name: str, message: str):
        log_time = clr.black(datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"))
        print(f"{log_time} {func(type)}    {clr.magenta(name)} {message}")

    # add slash commands
    async def setup_hook(self) -> None:
        initial_extensions = [
            "cogs." + command_file[:-3]
            for command_file in os.listdir("cogs")
            if command_file not in ["__pycache__", "__init__.py"]
        ]

        for extension in initial_extensions:
            await self.load_extension(extension)

        sync = await self.tree.sync()

        self.log('Info', clr.blue, 'Cogs', f"{len(sync)} Slash Command(s) Synced")

    async def on_ready(self):
        self.log('Info', clr.blue, 'Bot', f'Logged in as {self.user}')

        deadline.start(self)
        weekly_data.start()
        geek_of_the_week.start(self)
        leaderboard.start(self)

    async def on_message(self, message: discord.Message):
        def is_student_of(class_name: str, author: discord.Member | discord.User):
            if not isinstance(message.author, discord.member.Member):
                return False

            for role in author.roles:
                if class_name in role.name.lower():
                    return True

            return False

        if message.author == self.user:
            return

        if message.content.startswith(self.user.mention):
            await message.channel.send("I'm here!")

        elif message.content.lower() in ["salam", "hello", "hi", "hey", "good morning"]:
            await message.channel.send(
                f"{message.author.mention}, great to see you {'coding' if is_student_of("coding", message.author) else 'here'}!"
            )


load_dotenv()
TOKEN = os.getenv("TOKEN")


if __name__ == "__main__":
    bot = Bot()
    if TOKEN:
        bot.run(TOKEN)
    else:
        bot.log('Error', clr.red, 'Bot', '.env missed TOKEN')
