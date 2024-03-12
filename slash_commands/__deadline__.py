import discord
from discord.ext import commands
from datetime import datetime, timedelta, UTC
from models import DeadData
from utils import color


class Deadline(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="deadline", description="set a deadline")
    @discord.app_commands.default_permissions(administrator=True)
    @discord.app_commands.describe(
        channel="channel to close",
        day="dealine day",
        hours="Enter dead hour in UTC timezone",
        minutes="Enter dead minutes in UTC timezone",
    )
    @discord.app_commands.choices(
        day=[
            discord.app_commands.Choice(
                name=(datetime.now(UTC) + timedelta(day)).strftime("%A"),
                value=str((datetime.now(UTC) + timedelta(day)).date()),
            )
            for day in range(7)
        ]
    )
    async def deadline_command(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        day: str,
        hours: discord.app_commands.Range[int, 0, 23],
        minutes: discord.app_commands.Range[int, 0, 59],
    ):
        await interaction.response.defer()
        deadtime = datetime.fromisoformat(f"{day} {hours:0>2}:{minutes:0>2}:00+00:00")

        try:
            DeadData.create(channel=channel.id, time=deadtime)
        except FileExistsError:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=color.red,
                    description=f"the channel: {channel.mention} already dead!",
                )
            )
            return

        await interaction.followup.send(
            embed=discord.Embed(
                color=color.blue,
                description=f"channel: {channel.mention}\ndeadtime: <t:{int(deadtime.timestamp())}:F>\nEnds in: <t:{int(deadtime.timestamp())}:R>",
            )
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Deadline(bot))
