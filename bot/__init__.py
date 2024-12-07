import discord
import os
import contexts
import tasks
from discord.ext import commands
from utils import clr
from typing import Literal
from datetime import datetime, UTC
from bot.config import GUILD, USERS
from config import get_channel


class Bot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix="-", intents=discord.Intents.all())

    def log(
        self, type: Literal["Info", "Error", "Task"], func, name: str, message: str
    ):
        log_time = clr.black(datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"))
        print(
            f"{log_time} {func(type)}{' ' * (8 - len(type))} {clr.magenta(name)} {message}"
        )

    async def setup_hook(self) -> None:
        initial_extensions = [
            "cogs." + command_file[:-3]
            for command_file in os.listdir("cogs")
            if command_file not in ["__pycache__", "__init__.py"]
        ]

        for extension in initial_extensions:
            await self.load_extension(extension)

        sync = await self.tree.sync()

        self.log("Info", clr.blue, "Cogs", f"{len(sync)} Slash Command(s) Synced")

    async def on_ready(self):
        self.log("Info", clr.blue, "Bot", f"Logged in as {self.user}")
        tasks.start(self)

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
            message_content = (
                message.content.strip().replace(self.user.mention, "").lower()
            )

            if message_content == "":
                answer = "I'm here!"
            elif message_content in ["salam", "hello", "hi", "hey", "good morning"]:
                answer = f"{message.author.mention}, great to see you {'coding' if is_student_of("coding", message.author) else 'here'}!"
            else:
                answer = "^_^"

            await message.channel.send(answer)
            return

        if message.author.id == USERS.fariesus:
            await contexts.run(self, message)

    async def on_member_join(self, member: discord.Member):
        if member.guild.id != GUILD:
            return

        if welcome_channel_id := get_channel("welcome") is None:
            self.log("Error", clr.red, "Bot", "welcome channel id not found")
            return

        if welcome_channel := self.get_channel(welcome_channel_id) is None:
            self.log("Error", clr.red, "Bot", "welcome channel not found")
            return

        await welcome_channel.send(
            content=f"Hey {member.mention}, welcome to **{member.guild}**!"
        )
