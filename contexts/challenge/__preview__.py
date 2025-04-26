from typing import Any, Coroutine

import discord
from discord.ext import commands

from config import get_challenge_by_name, get_emoji
from consts import COLOR
from utils import number

__OWNER_ONLY__ = True
__DESCRIPTION__ = "Preview a challenge"


async def __run__(
    *, bot: commands.Bot, message: discord.Message, language: str, name: str
) -> Coroutine[Any, Any, None]:
    if (challenge := get_challenge_by_name(language, name)) is None:
        await message.reply(
            embed=discord.Embed(
                color=COLOR.red,
                title="Challenge not found",
                description=(f"**`Language`**: {language}\n" f"**`Name`**: {name}"),
            ),
            delete_after=11,
        )
        await message.delete(delay=11)
        return
    await message.reply(
        embed=discord.Embed(
            color=COLOR.yellow,
            title=challenge.name,
            description=(
                f"```ansi\n{challenge.subject}```\n"
                f"**`Level`**: {challenge.level}\n"
                f"**`Reward`**: {number(challenge.coins)} {get_emoji("coin")}\n"
                f"**`Excpected File`**: {challenge.file}"
            ),
        ).set_footer(text="as always follow the law and doubt your code!"),
        mention_author=False,
    )
