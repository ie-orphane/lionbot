from typing import Any, Coroutine

import discord
from discord.ext import commands

from consts import COLOR, GOLDEN_RATIO

__OWNER_ONLY__ = True
__DESCRIPTION__ = "Show the calculation of outlist event cost."


async def __run__(
    *, bot: commands.Bot, message: discord.Message
) -> Coroutine[Any, Any, None]:
    embed = discord.Embed(
        color=COLOR.blue,
        description=(
            "**Expression**```Φ ^ ((Δ + Φ) / Φ)) * (Π * Φ)```\n**Values**```"
            f"Φ  :  GOLDEN_RATIO  :  {GOLDEN_RATIO}\n"
            "Δ  :  ORDINAL_DAY   :  day of the week\n"
            "Π  :  RANDOM_PRIME  :  random prime number```\n**Summary**```"
        ),
    ).set_footer(text="calculation  -  outlist  -  event")

    data = sorted(
        [
            (
                day,
                prime,
                (GOLDEN_RATIO ** ((day + GOLDEN_RATIO) / GOLDEN_RATIO))
                * (prime * GOLDEN_RATIO),
            )
            for day in range(5)
            for prime in [5, 7, 11, 13]
        ],
        key=lambda x: x[-1],
    )

    maxf = 0
    for _, _, amount in data:
        maxf = max(0, len(str(amount)[: str(amount).index(".")]))
    for line in data:
        embed.description += (
            f"{line[0]}  |  "
            f"{line[1]:>2}  |  "
            f"{' ' * (maxf - len(str(line[2])[:str(line[2]).index('.')]))}{line[2]}"
            "\n"
        )
    embed.description += "```"

    await message.reply(embed=embed, mention_author=False)
