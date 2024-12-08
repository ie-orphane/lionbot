import discord
from discord.ext import commands
from .__all__ import contexts


async def run(bot: commands.Bot, message: discord.Message) -> None:
    context, *args = message.content.lower().split()

    if len(context) == 0:
        return

    ctx, count = contexts.get(context, (None, 0))

    if ctx is not None:
        args.insert(0, message)
        await ctx(*(args[:count]))
        return
