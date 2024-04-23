import discord
from discord.ext import commands
from datetime import datetime, timedelta, UTC
from models import ChannelData
from utils import dclr
from typing import Literal


class Deadline(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="deadline", description="set a deadline")
    @discord.app_commands.default_permissions(administrator=True)
    @discord.app_commands.guild_only()
    # @discord.app_commands.choices(
    #     day=[
    #         discord.app_commands.Choice(name=week_day, value=index)
    #         for index, week_day in enumerate(
    #             [
    #                 "Sunday",
    #                 "Monday",
    #                 "Tuesday",
    #                 "Wednesday",
    #                 "Thursday",
    #                 "Friday",
    #                 "Saturday",
    #             ]
    #         )
    #     ]
    # )
    @discord.app_commands.describe(
        channel="channel to close",
        day="Enter dead day",
        hours="Enter dead hour in UTC timezone",
        minutes="Enter dead minutes in UTC timezone",
    )
    async def deadline_command(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        role: discord.Role,
        day: Literal[
            "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
        ],
        hours: discord.app_commands.Range[int, 0, 23],
        minutes: discord.app_commands.Range[int, 0, 59],
    ):
        await interaction.response.defer()

        if ChannelData.exists(channel.id):
            await interaction.followup.send(
                embed=discord.Embed(
                    color=dclr.red,
                    description=f"### the channel: {channel.mention} already dead!",
                ),
                ephemeral=True,
            )
            return

        # day_select = discord.ui.Select(
        #     options=[
        #         discord.SelectOption(
        #             label=str((datetime.now(UTC) + timedelta(days=i)).strftime("%A")),
        #             value=str((datetime.now(UTC) + timedelta(days=i)).date()),
        #         )
        #         for i in range(7)
        #     ],
        #     placeholder="Select Day",
        # )

        # async def day_callback(_interaction: discord.Interaction):
        days = {
            (datetime.now(UTC) + timedelta(days=day))
            .__format__("%A"): (datetime.now(UTC) + timedelta(days=day))
            .date()
            for day in range(7)
        }
        deadtime = datetime.fromisoformat(f"{days[day]} {hours:0>2}:{minutes:0>2}:00+00:00")

        ChannelData.create(id=channel.id, time=deadtime, role=role.id)

        # await interaction.followup.edit_message(
        #     message_id=message.id,
        #     content=None,
        #     embed=discord.Embed(
        #         color=dclr.blue,
        #         description=f"channel: {channel.mention}\ndeadtime: <t:{int(deadtime.timestamp())}:F>\nEnds in: <t:{int(deadtime.timestamp())}:R>",
        #     ),
        #     view=None,
        # )
        await interaction.followup.send(
            embed=discord.Embed(
                color=dclr.yellow,
                description=f"channel: {channel.mention}\ndeadtime: <t:{int(deadtime.timestamp())}:F>\nEnds in: <t:{int(deadtime.timestamp())}:R>",
            )
        )

        # day_select.callback = day_callback

        # view = discord.ui.View(timeout=None)
        # view.add_item(day_select)

        # message = await interaction.followup.send(
        #     "## Select the deadline day:", view=view, ephemeral=True
        # )
        # message = await interaction.followup.send(
        #     "## Select the deadline day:", view=view, ephemeral=True
        # )


async def setup(bot: commands.Bot):
    await bot.add_cog(Deadline(bot))
