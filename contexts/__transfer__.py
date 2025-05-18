from typing import Any, Coroutine

import discord
from discord.ext import commands

from config import get_emoji
from consts import COLOR, TRANSFER_FEE
from models import UserData
from utils import number

__DESCRIPTION__ = "Transfer coins to your fellow geek(s)."


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
            title="❌ Transaction denied!",
            color=COLOR.red,
            description=f"✋ {message.author.mention},\n" + "\n".join(desc),
        )
    )


async def __run__(
    *,
    bot: commands.Bot,
    message: discord.Message,
    amount: int,
    members: list[discord.Member],
) -> Coroutine[Any, Any, None]:
    """
    Transfer coins to your fellow geek(s).
    Args:
        bot (commands.Bot): The bot instance.
        message (discord.Message): The message containing the command.
        amount (int): The amount of coins to transfer.
        members (list): List of members to whom the coins will be transferred.
    """

    if amount < 1:
        await __error(message, "the amount must be greater than or equal to **1**.")
        return

    if (user := UserData.read(message.author.id)) is None:
        await __error(
            message,
            "you need to register before using `>transfer`.",
            "Instead, use the `/register` command.",
        )
        return

    recipients = []

    for member in members:
        if members.count(member) > 1:
            await __error(
                message,
                f"you can't transfer coins to the {member.mention} multiple times!",
            )
            return

        if member.id == message.author.id:
            await __error(message, f"you can't transfer coins to yourself!")
            return

        if (recipient := UserData.read(member.id)) is None:
            await __error(message, f"{member.mention} is not registered yet!")
            return

        recipients.append(recipient)

    _amount = amount * len(recipients)
    fee = _amount * TRANSFER_FEE
    if (_amount + fee) > user.coins:
        await __error(
            message,
            f"you don't have {number(_amount + fee)} ({number(amount)}) {get_emoji('coin')}!",
            f"Your current balance is {number(user.coins)} {get_emoji('coin')}.",
        )
        return

    user.sub_coins(_amount, "huge transfer")
    user.sub_coins(fee, "huge transfer fee")

    for recipient in recipients:
        recipient.add_coins(amount, "huge transfer")

    await message.reply(
        embed=discord.Embed(
            color=COLOR.yellow,
            title="✅ Transaction completed!",
            description=(
                f"`Amount`: {number(amount)} {get_emoji("coin")}\n"
                f"`Total`: {number(_amount)} {get_emoji("coin")}\n"
                f"`Fee`: {number(_amount * TRANSFER_FEE)} {get_emoji("coin")}\n"
                f"`Sender`: {message.author.mention}\n"
                f"`Recipient(s)`: {', '.join([m.mention for m in members])}"
            ),
        ),
        mention_author=False,
    )
