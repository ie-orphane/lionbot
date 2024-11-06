import discord
from discord.ext import commands
from models import UserData, UserChallenge
from utils import RelativeDateTime


async def run(bot: commands.Bot, message: discord.Message) -> None:
    context = message.content.lower().split()

    if len(context) == 0:
        return

    if context[0] == "hello":
        await message.channel.send("hello chef!")
        return

    if context[0] == "help":
        await message.channel.send(
            "```txt\nhelp\nusers\nchallenges\nuser [key:id,login] <value>\n"
            "challenge [id,login] <value>```"
        )
        return

    if context[0] == "users":
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

    if context[0] == "challenges":
        language = "shell"
        for user in UserData.read_all():
            if user_challenges := user.challenges:
                all_challenges: dict[tuple[int, str], list[UserChallenge]] = {}

                for challenge in user_challenges:
                    if challenge.language == language:
                        all_challenges.setdefault((challenge.level, challenge.name), [])
                        all_challenges[(challenge.level, challenge.name)].append(
                            challenge
                        )
                if current_challenge := user.challenge:
                    if current_challenge.language == language:
                        all_challenges.setdefault(
                            (current_challenge.level, current_challenge.name), []
                        )
                        current_challenge.result = "CURRENT"
                        all_challenges[
                            (current_challenge.level, current_challenge.name)
                        ].append(current_challenge)

                all_challenges = dict(
                    sorted(all_challenges.items(), key=lambda x: x[0][0])
                )

                solved = 0
                content = ""
                for challenge_info, challenges in all_challenges.items():
                    challenges.sort(key=lambda x: x.attempt)
                    content += f"\n{challenge_info[0]} : {challenge_info[1]}\n"
                    for challenge in challenges:
                        if challenge.result == "OK":
                            solved += 1
                        content += f"\t [{challenge.attempt}]  {challenge.result:^9}  {RelativeDateTime(challenge.requested).pretty}\t\n"
                content = (
                    f"Total  : {len(all_challenges)}\nSolved : {solved}\n{content}"
                )

                await message.channel.send(
                    embed=discord.Embed(
                        title=user.name, description=f"```txt\n{content}\n```"
                    )
                )

    if len(context) == 2:
        return

    # user [key:id,login] <value>
    if context[0] == "user":
        key = context[1]
        value = context[2]
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

    # challenge [id,login] <value>
    if context[0] == "challenge":
        key = context[1]
        value = context[2]
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
