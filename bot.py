import discord, os
from dotenv import load_dotenv
from discord.ext import commands
from tasks import leaderboard, geek_of_the_week, weekly_data

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix="-", intents=discord.Intents.all())


    # add slash commands
    async def setup_hook(self: commands.Bot) -> None:
        initial_extensions = [
            "slash_commands." + command_file[:-3]
            for command_file in os.listdir("slash_commands")
            if command_file not in ["__pycache__", "__init__.py"]
        ]
        
        for extension in initial_extensions:
            await self.load_extension(extension)

        sync = await self.tree.sync()
        print(f"{len(sync)} Slash Command(s) Synced")

    async def on_ready(self):
        print(f"\nWe have logged in as {self.user}")

        weekly_data.start()
        # geek_of_the_week.start(self)
        # leaderboard.start(self)

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

        elif message.content.lower() in ["hello", "hi", "hey", "good morning"]:
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
    Bot().run(TOKEN)
