import discord
import traceback
import env
import os
from discord.ext import commands
from consts import COLOR
from datetime import datetime, UTC
from bot import Bot


class __Cog:
    color = COLOR

    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = bot

    async def cog_app_command_error(
        self,
        interaction: discord.Interaction,
        error: discord.app_commands.AppCommandError,
    ):
        log_id = int(datetime.now(UTC).timestamp())
        log_dir = f"{env.BASE_DIR}/storage/errors"
        with open(f"{log_dir}/{log_id}.log", "w") as file:
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
            return

        await error_channel.send(
            embed=discord.Embed(
                color=self.color.red,
                description=(
                    f"User: {interaction.user.mention} ({interaction.user.id})\n"
                    f"Command: /{interaction.command.qualified_name} ({interaction.id})\n"
                    f"Server: {interaction.guild} #{interaction.channel}\n"
                    f"Log: `{log_id}`\n"
                    f"Error: {error}\n"
                    f"```\n{traceback.format_exc()}\n```"
                ),
            )
        )

    def cog_interaction(self, interaction: discord.Interaction, **params):
        better = lambda x: '"' + x + '"' if isinstance(x, str) and " " in x else x
        with open(
            os.path.join(os.path.abspath(env.BASE_DIR), "data", "interactions.csv"), "a"
        ) as f:
            print(
                better(datetime.now(UTC)),
                interaction.user.id,
                better(interaction.user.display_name),
                better(interaction.command.qualified_name),
                *[f"{key}:{better(value)}" for key, value in params.items()],
                file=f,
                sep=",",
            )


class Cog(__Cog, commands.Cog): ...


class GroupCog(__Cog, commands.GroupCog): ...
