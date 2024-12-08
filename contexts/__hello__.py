import discord


async def hello(message: discord.Message) -> None:
    await message.channel.send("hello chef!")
