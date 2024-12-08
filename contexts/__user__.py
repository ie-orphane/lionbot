import discord
from models import UserData


async def user(message: discord.Message, key: str, value: str) -> None:
    user = None

    match key:
        case "id":
            user = UserData.read(value)
        case "login":
            for user_data in UserData.read_all():
                if (
                    "-".join([word[:3].lower() for word in user_data.name.split()])
                    == value
                ):
                    user = user_data
        case _:
            await message.channel.send(f"Unkown Proprety : {key}")
            return

    if user is None:
        await message.channel.send(f"Not found : {value}")
        return

    await message.channel.send(
        content=(
            f"**Name** : {user.name}\n**Id** : {user.id}\n"
            f"**Login** : {'-'.join([word[:3].lower() for word in user.name.split()])}\n"
            f"**Coins** : {user.name}\n**Training**: {user.training}\n"
        )
    )
