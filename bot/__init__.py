import discord
import os
import contexts as ctx
import tasks
from discord.ext import commands
from utils import log
from config import get_channel, get_config, get_user


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=".", intents=discord.Intents.all())

    async def setup_hook(self) -> None:
        initial_extensions = [
            "cogs." + command_file[:-3]
            for command_file in os.listdir("cogs")
            if command_file not in ["__pycache__", "__init__.py"]
        ]

        for extension in initial_extensions:
            await self.load_extension(extension)

        sync = await self.tree.sync()

        log("Info", "blue", "Cogs", f"{len(sync)} Slash Command(s) Synced")

    async def on_ready(self):
        log("Info", "blue", "Bot", f"Logged in as {self.user}")
        log("Info", "blue", "Contexts", f"{len(ctx.all_contexts)} Command(s)")
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

        if (owner_id := get_user("owner")) is None:
            log("Error", "red", "Bot", "owner id not found")
            return

        if message.author.id == owner_id:
            await ctx.run(self, message)

    async def on_member_join(self, member: discord.Member):
        if (guild_id := get_config("GUILD")) is None:
            log("Error", "red", "Bot", "guild id not found")
            return

        if member.guild.id != guild_id:
            return

        if welcome_channel_id := get_channel("welcome") is None:
            log("Error", "red", "Bot", "welcome channel id not found")
            return

        if welcome_channel := self.get_channel(welcome_channel_id) is None:
            log("Error", "red", "Bot", "welcome channel not found")
            return

        await welcome_channel.send(
            content=f"Hey {member.mention}, welcome to **{member.guild}**!"
        )
