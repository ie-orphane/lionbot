from typing import Any, Coroutine

import discord
from discord.ext import commands

from consts import COLOR

from .__all__ import all_contexts as ALL_CTXS


async def __run__(
    *, bot: commands.Bot, message: discord.Message
) -> Coroutine[Any, Any, None]:
    embed = (
        discord.Embed(
            color=COLOR.yellow,
            description=f"{bot.user.display_name} is a tool built to help you track your stats and improve your coding skills.",
        )
        .set_author(
            name=f"Salam {message.author.display_name} !",
            icon_url=message.author.display_avatar.url,
        )
        .set_footer(text="Also try /help")
    )

    for ctx in ALL_CTXS.values():
        if ctx.name == "help":
            continue

        embed.description += "\n\n" + ctx.usage
        if ctx.desc:
            embed.description += f"\n\t{ctx.desc}"

    await message.reply(embed=embed, mention_author=False)
