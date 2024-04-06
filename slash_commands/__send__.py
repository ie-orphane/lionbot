import discord
from discord.ext import commands
from datetime import datetime, UTC, timedelta
from utils import color
from models import FileData


class Send(commands.Cog):
    @discord.app_commands.command(name="send", description="send a file")
    @discord.app_commands.default_permissions(administrator=True)
    @discord.app_commands.guild_only()
    @discord.app_commands.describe(
        file="file to send",
        channel="channel to send file on",
        hours="Enter hour to send in UTC timezone",
        minutes="Enter minutes to send in UTC timezone",
    )
    async def send_command(
        self,
        interaction: discord.Interaction,
        file: discord.Attachment,
        channel: discord.TextChannel,
        hours: discord.app_commands.Range[int, 0, 23],
        minutes: discord.app_commands.Range[int, 0, 59],
    ):

        if FileData.exists(file.filename):
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=color.red,
                    description=f"### the file: {file.filename} already there!",
                ),
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        day_select = discord.ui.Select(
            options=[
                discord.SelectOption(
                    label=str((datetime.now(UTC) + timedelta(days=i)).strftime("%A")),
                    value=str((datetime.now(UTC) + timedelta(days=i)).date()),
                )
                for i in range(7)
            ],
            placeholder="Select Day",
        )

        async def day_callback(_interaction: discord.Interaction):
            deadtime = datetime.fromisoformat(
                f"{day_select.values[0]} {hours:0>2}:{minutes:0>2}:00+00:00"
            )

            await file.save(f"./assets/files/{file.filename}")
            FileData.create(channel=channel.id, time=deadtime, name=file.filename)

            await interaction.followup.edit_message(
                message_id=message.id,
                content=None,
                embed=discord.Embed(
                    color=color.blue,
                    description=f"channel: {channel.mention}\nsendtime: <t:{int(deadtime.timestamp())}:F>\nSends in: <t:{int(deadtime.timestamp())}:R>",
                ),
                view=None,
            )

        day_select.callback = day_callback

        view = discord.ui.View(timeout=None)
        view.add_item(day_select)

        message = await interaction.followup.send(
            "## Select the send day:", view=view, ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Send(bot))
