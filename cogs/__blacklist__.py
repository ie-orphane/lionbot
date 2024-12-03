import math
import discord
import datetime as dt
from discord.ext import commands
from models import UserData
from utils import COLOR, open_file, get_week
from bot.config import Emoji

GOLDEN_RATIO = (1 + math.sqrt(5)) / 2
AMOUNT = GOLDEN_RATIO ** 11


@discord.app_commands.guild_only()
class Blacklist(commands.GroupCog, name="blacklist"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.color = COLOR

    @discord.app_commands.command(description="get out of the blacklist")
    async def out(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user = UserData.read(interaction.user.id)

        if user is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, you are not registered yet!",
                ).set_footer(text="use /register instead")
            )
            return

        black_list_role = None

        # get Geek of the week and black list roles
        for role in interaction.guild.roles:
            if role.name == "Black List":
                black_list_role = role

        # if not found create new one
        if (
            black_list_role is None
            or interaction.user.get_role(black_list_role.id) is None
        ):
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, we can't find you in blacklist.",
                ).set_footer(text="wanna join us?")
            )
            return

        this_week = get_week()
        weeks = open_file("data/blacklist.json")
        current_week = weeks.get(str(this_week.count))

        if current_week is None:
            if user.coins < AMOUNT:
                await interaction.followup.send(
                    embed=discord.Embed(
                        color=self.color.red,
                        description=f"{interaction.user.mention}, you don't have ehough coins!\nYou need **{AMOUNT - user.coins}** {Emoji.coin} more.",
                    )
                )
                return
        
            await interaction.user.remove_roles(black_list_role)

            user.sub_coins(current_week["amout"], "blacklist out")

            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.green,
                    description=f"{interaction.user.mention}, congarts 🥳!\nYou are free now.\nYou paied {AMOUNT} {Emoji.coin}.",
                ),
            )
            return

        if geeK_id := current_week["claimed_by"]:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, the event already finished\nClaimed by <@{geeK_id}>.",
                ).set_footer(text="maybe the next week!")
            )
            return

        now = dt.datetime.now(dt.UTC).replace(second=0, microsecond=0)
        if now < dt.datetime.fromisoformat(current_week["datetime"]):
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, the event didn't started yet ⏲️.",
                ).set_footer(text="be patient!")
            )
            return

        if now > dt.datetime.fromisoformat(current_week["datetime"]) + dt.timedelta(
            seconds=current_week["ends_in"]
        ):
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, the event already finished ⏰.",
                ).set_footer(text="maybe next week!")
            )
            return
        
        if user.coins < current_week["amout"]:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, you need {current_week["amout"] - user.coins} {Emoji.coin} more.",
                )
            )
            return

        await interaction.user.remove_roles(black_list_role)

        current_week["claimed_by"] = interaction.user.id
        user.sub_coins(current_week["amout"], "blacklist out")
        open_file("data/blacklist.json", weeks)

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                description=f"{interaction.user.mention}, congarts 🥳!\nYou paied {current_week["amout"]} {Emoji.coin}\nYou are free now.",
            ),
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Blacklist(bot))
