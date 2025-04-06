import subprocess

import discord
from discord.ext import commands

from consts import COLOR

__OWNER_ONLY__ = True
__DESCRIPTION__ = "Show Git history."


async def __run__(*, bot: commands.Bot, message: discord.Message, number: int = 7):
    try:
        result = subprocess.run(
            f"git fetch && git log --oneline -{number} --color=always --decorate=short",
            shell=True,
            text=True,
            capture_output=True
        )
    except Exception as e:
        await message.reply(
            embed=discord.Embed(
                color=COLOR.red, title="Error", description=f"```\n{e}\n```"
            ),
            delete_after=11,
        )
        await message.delete(delay=11)
        return

    await message.reply(
        embed=discord.Embed(
            color=COLOR.yellow,
            description=f"```ansi\n{result.stdout.replace("[m", "[0m")}\n```",
        ),
        mention_author=False,
    )
