import discord
from models import UserData


async def users(message: discord.Message) -> None:
    MAX = 23
    users = UserData.read_all()
    count, rest = divmod(len(users), MAX)
    start = 0
    for _ in range(count):
        data = "\n".join(
            [
                f"{user.name:<25} {'-'.join([word[:3].lower() for word in user.name.split()])}"
                for user in users[start : (start + MAX)]
            ]
        )
        await message.channel.send(f"{data}")
        start += MAX
    if rest != 0:
        data = "\n".join(
            [
                f"{user.name:<25} {'-'.join([word[:3].lower() for word in user.name.split()])}"
                for user in users[start:]
            ]
        )
        await message.channel.send(f"{data}")
