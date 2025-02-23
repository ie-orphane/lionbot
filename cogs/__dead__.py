import discord
import env
from discord.ext import commands
from models import ChannelData, FileData
from typing import Literal
from datetime import datetime, UTC, timedelta
from cogs import GroupCog


@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
class Dead(GroupCog, name="dead"):
    @discord.app_commands.command(description="Send a channel to death.")
    @discord.app_commands.describe(
        channel="The channel to close.",
        day="The channel's dead day.",
        hours="The channel's dead hour in UTC timezone.",
        minutes="The channel's dead minutes.",
    )
    async def channel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        role: discord.Role,
        day: Literal[
            "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
        ],
        hours: discord.app_commands.Range[int, 0, 23],
        minutes: discord.app_commands.Range[int, 0, 59] = 0,
    ):
        await interaction.response.defer()

        if ChannelData.exists(channel.id):
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"### the channel: {channel.mention} already dead!",
                ),
                ephemeral=True,
            )
            return

        days = {
            (datetime.now(UTC) + timedelta(days=day))
            .__format__("%A"): (datetime.now(UTC) + timedelta(days=day))
            .date()
            for day in range(7)
        }
        deadtime = datetime.fromisoformat(
            f"{days[day]} {hours:0>2}:{minutes:0>2}:00+00:00"
        )

        ChannelData.create(id=channel.id, time=deadtime, role=role.id)

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.yellow,
                description=f"channel: {channel.mention}\ndeadtime: <t:{int(deadtime.timestamp())}:F>\nEnds in: <t:{int(deadtime.timestamp())}:R>",
            )
        )

    @discord.app_commands.command(description="Send a file to death.")
    @discord.app_commands.describe(
        file="file to send",
        channel="channel to send file on",
        day="The file's dead day",
        hours="The file's hour to send in UTC timezone",
        minutes="The file's dead minutes.",
    )
    async def file(
        self,
        interaction: discord.Interaction,
        file: discord.Attachment,
        channel: discord.TextChannel,
        day: Literal[
            "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
        ],
        hours: discord.app_commands.Range[int, 0, 23],
        minutes: discord.app_commands.Range[int, 0, 59] = 0,
    ):
        await interaction.response.defer()

        days = {
            (datetime.now(UTC) + timedelta(days=day))
            .__format__("%A"): (datetime.now(UTC) + timedelta(days=day))
            .date()
            for day in range(7)
        }
        deadtime = datetime.fromisoformat(
            f"{days[day]} {hours:0>2}:{minutes:0>2}:00+00:00"
        )
        filename = f"{interaction.user.id}-{int(datetime.now(UTC).timestamp())}.{file.filename.split('.')[-1]}"

        await file.save(f"{env.BASE_DIR}/storage/files/{filename}")
        FileData.create(id=filename, channel=channel.id, time=deadtime)

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.yellow,
                description=f"channel: {channel.mention}\nsendtime: <t:{int(deadtime.timestamp())}:F>\nSends in: <t:{int(deadtime.timestamp())}:R>",
            ),
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Dead(bot))
