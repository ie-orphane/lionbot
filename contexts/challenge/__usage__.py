from typing import Any, Coroutine

import discord
from discord.ext import commands

from models import UserChallenge, UserData
from utils import RelativeDateTime

__OWNER_ONLY__ = True
__DESCRIPTION__ = "show challenge solved by user"


async def __run__(
    *, bot: commands.Bot, message: discord.Message
) -> Coroutine[Any, Any, None]:
    for user in UserData.read_all():
        if user_challenges := user.challenges:
            all_challenges: dict[tuple[int, str], list[UserChallenge]] = {}

            for challenge in user_challenges:
                all_challenges.setdefault((challenge.level, challenge.name), [])
                all_challenges[(challenge.level, challenge.name)].append(challenge)
            if current_challenge := user.challenge:
                all_challenges.setdefault(
                    (current_challenge.level, current_challenge.name), []
                )
                current_challenge.result = "CURRENT"
                all_challenges[
                    (current_challenge.level, current_challenge.name)
                ].append(current_challenge)

            all_challenges = dict(sorted(all_challenges.items(), key=lambda x: x[0][0]))

            solved = 0
            content = ""
            for challenge_info, challenges in all_challenges.items():
                challenges.sort(key=lambda x: x.attempt)
                content += f"\n{challenge_info[0]} : {challenge_info[1]}\n"
                for challenge in challenges:
                    if challenge.result == "OK":
                        solved += 1
                content += f"\t [{challenge.attempt}]  {challenge.result:^9}  {RelativeDateTime(challenge.requested).pretty}\t\n"

            await message.channel.send(
                embed=discord.Embed(
                    title=f"{user.name} : {solved} / {len(all_challenges)}",
                    description=f"```txt\n{content}\n```",
                )
            )
