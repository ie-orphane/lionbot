import env
import traceback
import discord
from consts import COLOR
from datetime import datetime, UTC


async def on_error(self, interaction: discord.Interaction, error: Exception, name: str):
    log_id = int(datetime.now(UTC).timestamp())
    log_dir = f"{env.BASE_DIR}/storage/errors"
    with open(f"{log_dir}/{log_id}.log", "w") as file:
        file.writelines(
            [
                f"User: {interaction.user.display_name} ({interaction.user.id})\n",
                f"Interaction: {name} ({interaction.id})\n",
                f"Server: {interaction.guild} #{interaction.channel}\n",
                f"Error: {error}\n",
            ]
        )
        traceback.print_exc(file=file)

    try:
        await interaction.followup.send(
            embed=discord.Embed(
                color=COLOR.red,
                description=(
                    "**Oops!** The bot sometimes takes a nap. 💤\n"
                    "Don't worry, we'll fix the issue as soon as possible!\n\n"
                    f"📝 **Error ID:** `{log_id}`"
                ),
            ).set_footer(
                text="If this error occurs multiple times, please contact the owner."
            )
        )
    except discord.NotFound:
        await interaction.user.send(
            embed=discord.Embed(
                color=COLOR.red,
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
            color=COLOR.red,
            description=(
                f"User: {interaction.user.mention} ({interaction.user.id})\n"
                f"Interaction: {name} ({interaction.id})\n"
                f"Server: {interaction.guild} #{interaction.channel}\n"
                f"Log: `{log_id}`\n"
                f"Error: {error}\n"
                f"```\n{traceback.format_exc()}\n```"
            ),
        )
    )
