import os
import discord
import traceback
from utils import Log
from discord.ext import commands
from constants import COLOR
from datetime import datetime, UTC


class Cog(commands.Cog):
    color = COLOR

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot


class GroupCog(commands.GroupCog):
    color = COLOR

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    async def cog_app_command_error(
        self,
        interaction: discord.Interaction,
        error: discord.app_commands.AppCommandError,
    ):
        log_id = int(datetime.now(UTC).timestamp())
        log_dir = "./data/errors"
        os.makedirs(log_dir, exist_ok=True)
        with open(f"/{log_id}.log", "w") as file:
            file.writelines(
                [
                    f"User: {interaction.user.display_name} ({interaction.user.id})\n",
                    f"Command: /{interaction.command.qualified_name} ({interaction.id})\n",
                    f"Server: {interaction.guild} #{interaction.channel}\n",
                    f"Error: {error}\n",
                ]
            )
            traceback.print_exc(file=file)

        await interaction.channel.send(
            embed=discord.Embed(
                color=self.color.red,
                description=(
                    "**Oops!** The bot sometimes takes a nap. 💤\n"
                    "Don't worry, we'll fix the issue as soon as possible!\n\n"
                    f"📝 **Error ID:** `{log_id}`"
                ),
            ).set_footer(
                text="If this error occurs multiple times, please contact the owner."
            )
        )

        if (error_channel := self.bot.get_listed_channel("error")) is None:
            Log.error("Project", "error while getting error channel")
            return

        await error_channel.send(
            embed=discord.Embed(
                color=self.color.red,
                description=(
                    f"User: {interaction.user.display_name} ({interaction.user.id})\n"
                    f"Command: /{interaction.command.qualified_name} ({interaction.id})\n"
                    f"Server: {interaction.guild} #{interaction.channel}\n"
                    f"Log: `{log_id}`\n"
                    f"Error: {error}\n"
                    f"```\n{traceback.format_exc()}\n```"
                ),
            ).set_footer(
                text="If this error occurs multiple times, please contact the owner."
            )
        )
