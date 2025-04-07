from typing import Any, Coroutine

import discord
from discord.ext import commands

from config import get_emojis
from consts import COLOR
from models import UserData
from utils import number

__OWNER_ONLY__ = True
__DESCRIPTION__ = "Show stats around the application."


async def __run__(
    *, bot: commands.Bot, message: discord.Message
) -> Coroutine[Any, Any, None]:
    emojis = get_emojis("coin", "1st", "2nd", "3rd", "empty")

    total_coins = 0
    total_users = 0
    users: list[UserData] = UserData.read_all()
    top_users_by_coins = "".join(
        map(
            lambda x: f"{emojis.empty}{emojis.empty}{x[0]} {x[1].name} (<@{x[1].id}>) {number(x[1].coins)} {emojis.coin}\n",
            list(
                zip(
                    [emojis["1st"], emojis["2nd"], emojis["3rd"]],
                    sorted(users, key=lambda x: x.coins, reverse=True),
                )
            ),
        )
    )
    for user in users:
        total_coins += user.coins
        total_users += 1

    embed = discord.Embed(
        color=COLOR.blue,
        description=(
            f"**Users**\n{emojis.empty}`total`: {total_users}\n\n"
            f"**Coins**\n{emojis.empty}`total`: {number(total_coins)} {emojis.coin}\n"
            f"{emojis.empty}`average`: {number(total_coins / total_users)} {emojis.coin}\n"
            f"{emojis.empty}`top`: \n{top_users_by_coins}"
        ),
    )

    await message.reply(embed=embed, mention_author=False)
