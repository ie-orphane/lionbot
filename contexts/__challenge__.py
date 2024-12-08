import discord
from models import UserData


async def challenge(message: discord.Message, key: str, value: str) -> None:
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

    for challenge in user.challenges:
        if challenge._solution:
            with open(challenge.solution, "r") as file:
                await message.channel.send(
                    embed=discord.Embed(
                        title=f"{challenge.level} : {challenge.name}",
                        description=f"```{challenge.extension}\n{file.read()}```",
                    )
                )
