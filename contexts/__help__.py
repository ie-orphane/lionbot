import discord


async def help(message: discord.Message) -> None:
    await message.channel.send(
        "```txt\nhelp\nusers\nchallenges\nuser [key:id,login] <value>\n"
        "challenge [id,login] <value>```"
    )
