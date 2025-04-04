import discord
import re
from discord.ext import commands
from .__all__ import all_contexts


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
    command, _options = parse(message.content)

    if (command is None) or ((ctx := all_contexts.get(command)) is None):
        return

    options = {"bot": bot, "message": message}

    for name, param in ctx.args.items():
        value = _options.get(name)

        if value is None:
            print(f"Missing argument: `{name}`")
            return

        try:
            value = param.annotation(value)
        except ValueError:
            print(f"Invalid argument type: `{name}`")
            return

        options[name] = value

    await ctx(**options)