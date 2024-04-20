import discord, os
from dotenv import load_dotenv
from discord.ext import commands
from tasks import leaderboard
from utils import clr
from datetime import datetime, UTC


class Bot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix="-", intents=discord.Intents.all())

    # add slash commands
    async def setup_hook(self: commands.Bot) -> None:
        initial_extensions = [
            "cogs." + command_file[:-3]
            for command_file in os.listdir("cogs")
            if command_file not in ["__pycache__", "__init__.py"]
        ]

        for extension in initial_extensions:
            await self.load_extension(extension)

        sync = await self.tree.sync()
        print(
            f"{clr.black(datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S'))} {clr.blue('Info')}     {clr.magenta('Cogs')}  {len(sync)} Slash Command(s) Synced"
        )

    async def on_ready(self):
        print(
            f"{clr.black(datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S'))} {clr.blue('Info')}     {clr.magenta('Bot')}  We have logged in as {self.user}"
        )

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
            if is_student_of("coding", message.author):
                await message.channel.send(
                    f"{message.author.mention}, great to see you coding!"
                )

            else:
                await message.channel.send(
                    f"{message.author.mention}, great to see you here!"
                )


load_dotenv()
TOKEN = os.getenv("TOKEN")


if __name__ == "__main__":
    if TOKEN:
        Bot().run(TOKEN)
    else:
        print(
            f"{clr.black(datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S'))} {clr.red('Error')}     {clr.magenta('Bot')}  .env missed TOKEN"
        )
