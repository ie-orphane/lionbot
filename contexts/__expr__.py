from typing import Any, Coroutine

import discord
from discord.ext import commands

from consts import COLOR, GOLDEN_RATIO
from utils import number

__DESCRIPTION__: str = "Evaluate an expression."
__ADMIN_ONLY__: bool = True


async def __error(
    message: discord.Message, *desc: tuple[str]
) -> Coroutine[Any, Any, None]:
    """
    Send an error message to the user.
    Args:
        message (discord.Message): The message containing the command.
        desc (tuple[str]): The error description.
    """
    await message.reply(
        embed=discord.Embed(
            color=COLOR.red,
            description=f"✋ {message.author.mention},\n" + "\n".join(desc),
        ),
        delete_after=64,
        mention_author=True,
    )
    await message.delete(delay=64)


async def __run__(
    *,
    bot: commands.Bot,
    message: discord.Message,
    expression: str,
) -> Coroutine[Any, Any, None]:
    options = {"GOLDEN_RATIO": GOLDEN_RATIO}
    try:
        _expression = expression.format(**options)
    except KeyError as e:
        await __error(message, f"**{e}** is an invalid key in `{expression}`.")
        return

    try:
        amount = float(eval(_expression))
    except Exception:
        await __error(
            message,
            f"Invalid syntax in `{expression}`.",
            "example of valid expression:",
            "`{GOLDEN_RATIO} * 11`.",
        )
        return

    await message.reply(
        embed=discord.Embed(
            color=COLOR.green,
            description=f"`{expression}` => `{_expression}` => {number(amount)}",
        ),
        mention_author=False,
    )
