import statistics
from typing import Any, Coroutine

import discord
from discord.ext import commands

from consts import COLOR
from models import UserData
from utils import charts, clr

__OWNER_ONLY__ = True
__DESCRIPTION__ = "Show lioncoin stats."


async def __run__(
    *, bot: commands.Bot, message: discord.Message
) -> Coroutine[Any, Any, None]:
    users: list[UserData] = UserData.read_all()

    coins = [user.coins for user in users]
    stats = {
        clr.yellow("Total  "): sum(coins),
        clr.blue("Minimum"): min(coins),
        clr.blue("Maximum"): max(coins),
        "\n" + clr.blue("Average"): statistics.mean(coins),
        clr.yellow("Middle "): statistics.median(coins),
        "\n" + clr.blue("Spread "): statistics.stdev(coins),
        clr.blue("Common "): statistics.mode(coins),
    }
    max_l = max(len(f"{value:,}".split(".")[0]) for value in stats.values())
    formatted_stats = {
        key: f"{' ' * (max_l - len(f"{value:,}".split('.')[0]))}{value:,}"
        for key, value in stats.items()
    }
    sorted_coins = sorted(coins)

    top_3 = [x.__format__(",") for x in sorted_coins[-3:][::-1]]
    max_top = max(len(value.split(".")[0]) for value in top_3)
    last_3 = [x.__format__(",") for x in sorted_coins[:3]]
    max_last = max(len(value.split(".")[0]) for value in last_3)

    embed = discord.Embed(
        color=COLOR.blue, description=f"```ansi\n", url="https://lionsgeek.ma"
    ).set_footer(text="📊 statistics - coins")
    for key, value in formatted_stats.items():
        embed.description += f"{key} :  {value}\n"
    embed.description += (
        f"\n{clr.green('Top')}     :{''.join(map(lambda x: f"\n  {' ' * (max_top - len(f"{x}".split('.')[0]))}{x}", top_3))}"
        f"\n{clr.red('Last')}    :{''.join(map(lambda x: f"\n  {' ' * (max_last - len(f"{x}".split('.')[0]))}{x}", last_3))}"
    )
    embed.description += "```"
    print(embed.description)

    files = []
    embeds = [embed]
    for path in [charts.coins_bar(users), charts.coins_line(users)]:
        files.append(discord.File(path, filename=path.split("/")[-1]))
        embeds.append(
            discord.Embed(color=COLOR.blue, url="https://lionsgeek.ma").set_image(
                url=f"attachment://{path.split('/')[-1]}"
            )
        )

    await message.reply(files=files, embeds=embeds, mention_author=False)
