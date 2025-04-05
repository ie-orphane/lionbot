import discord
from consts import COLOR
from discord.ext import commands
from models import UserData
from config import get_emoji
from utils import number
from typing import Coroutine, Any


description = "Transfer coins to your fellow geek(s)."


async def error(
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
            title="❌ Transaction denied!",
            color=COLOR.red,
            description=f"✋ {message.author.mention},\n" + "\n".join(desc),
        ),
        delete_after=11,
        mention_author=True,
    )
    await message.delete(delay=11)


async def run(
    *,
    bot: commands.Bot,
    message: discord.Message,
    amount: int,
    member: list[discord.Member],
) -> Coroutine[Any, Any, None]:
    """
    Transfer coins to your fellow geek(s).
    Args:
        bot (commands.Bot): The bot instance.
        message (discord.Message): The message containing the command.
        amount (int): The amount of coins to transfer.
        member (list): List of members to whom the coins will be transferred.
    """

    if amount < 1:
        await error(message, "the amount must be greater than or equal to **1**.")
        return

    if (user := UserData.read(message.author.id)) is None:
        await error(
            message,
            "you need to register before using `>transfer`.",
            "Instead, use the `/register` command.",
        )
        return

    recipient = []

    for m in member:
        if member.count(m) > 1:
            await error(
                message, f"you can't transfer coins to the {m.mention} multiple times!"
            )
            return

        if m.id == message.author.id:
            await error(message, f"you can't transfer coins to yourself!")
            return

        if (r := UserData.read(m.id)) is None:
            await error(message, f"{m.mention} is not registered yet!")
            return

        recipient.append(r)

    if (_amount := amount * len(recipient)) > user.coins:
        await error(
            message,
            f"you don't have {number(_amount)} ({number(amount)}) {get_emoji('coin')}!",
            f"Your current balance is {number(user.coins)} {get_emoji('coin')}.",
        )
        return

    user.sub_coins(amount, "huge transfer")
    user.update()

    for r in recipient:
        r.add_coins(amount, "huge transfer")
        r.update()

    await message.reply(
        embed=discord.Embed(
            color=COLOR.yellow,
            title="✅ Transaction completed!",
            description=(
                f"`Amount`: {number(amount)} {get_emoji("coin")}\n"
                f"`Total`: {number(_amount)} {get_emoji("coin")}\n"
                f"`Sender`: {message.author.mention}\n"
                f"`Recipient(s)`: {', '.join([m.mention for m in member])}"
            ),
        ),
        mention_author=False,
    )
