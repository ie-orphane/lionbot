import discord
import re
from discord.ext import commands
from .__all__ import all_contexts
from consts import COLOR
from typing import get_origin, get_args


def parse(context: str) -> tuple[str, dict]:
    """
    Parse a command string into a command and options.
    Args:
        context (str): The command string to parse.
    Returns:
        tuple: A tuple containing the command and a dictionary of options.
    """

    context = re.sub(r"\s+", " ", context).strip().lower()

    command = None
    options = {}

    match = re.match(r"^>([^\s`]+(?:\s+[^\s`]+)*)", context)
    if match:
        command = match.group(1).strip()

    options = {
        key: value.strip()
        for key, value in re.findall(r"`([a-zA-Z_]+)`\s*:\s*([^`]+)", context)
    }

    return (command, options)


async def run(bot: commands.Bot, message: discord.Message) -> None:
    """
    Run the command based on the message content.
    Args:
        bot (commands.Bot): The bot instance.
        message (discord.Message): The message containing the command.
    """

    command, _options = parse(message.content)

    if (command is None) or ((ctx := all_contexts.get(command)) is None):
        return

    options = {"bot": bot, "message": message}

    for name, param in ctx.args.items():
        value = _options.get(name)

        if value is None:
            await message.reply(
                embed=discord.Embed(
                    color=COLOR.red,
                    description=(
                        f"Missing argument: **`{name}`**\n" f"\nUsage: {ctx.usage}"
                    ),
                ),
                mention_author=True,
                delete_after=11,
            )
            await message.delete(delay=11)
            return

        if (origin := get_origin(param.annotation)) is None:
            try:
                value = param.annotation(value)
            except ValueError:
                await message.reply(
                    embed=discord.Embed(
                        color=COLOR.red,
                        description=(
                            f"Invalid argument  value: **`{value}`** for `{name}`.\n"
                            f"\nExpected type: **`{param.annotation.__name__}`**"
                        ),
                    ),
                    mention_author=True,
                    delete_after=11,
                )
                await message.delete(delay=11)
                return
        elif origin is list:
            value = value.split(",")
            if discord.Member in (args := get_args(param.annotation)):
                members = []
                for i, m in enumerate(value):
                    if m.strip() == "":
                        continue
                    if re.match(r"^<@!?(\d+)>$", m.strip()) or re.match(
                        r"^\d+$", m.strip()
                    ):
                        user_id = int(re.sub(r"[<@!>]", "", m.strip()))
                        try:
                            members.append(
                                await bot.fetch_user(
                                    int(re.sub(r"[<@!>]", "", m.strip()))
                                )
                            )
                        except discord.NotFound:
                            await message.reply(
                                embed=discord.Embed(
                                    color=COLOR.red,
                                    description=(f"Member not found: <@{user_id}>"),
                                ),
                                mention_author=True,
                                delete_after=11,
                            )
                            await message.delete(delay=11)
                            return
                    else:
                        await message.reply(
                            embed=discord.Embed(
                                color=COLOR.red,
                                description=(
                                    f"Invalid value: **`{m}`** for `{name}`.\n"
                                    f"\nExcepted types: **`Member.mention`** | **`Member.id`**"
                                ),
                            ),
                            mention_author=True,
                            delete_after=11,
                        )
                        await message.delete(delay=11)
                        return
                value = members

        options[name] = value

    await ctx(**options)
