import discord
from discord.ext import commands
from models import UserData
from utils import COLOR, open_file, get_week
import datetime as dt


@discord.app_commands.default_permissions(send_messages=False)
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
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, no event for this week.",
                ).set_footer(text="maybe the next week!")
            )
            return

        if geeK_id := current_week["claimed_by"]:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, the event already claimed by <@{geeK_id}>.",
                ).set_footer(text="maybe the next week!")
            )
            return

        now = dt.datetime.now(dt.UTC).replace(second=0, microsecond=0)
        if now < dt.datetime.fromisoformat(current_week["datetime"]):
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, the event didn't started yet.",
                ).set_footer(text="be patient!")
            )
            return

        if now > dt.datetime.fromisoformat(current_week["datetime"]) + dt.timedelta(
            seconds=current_week["ends_in"]
        ):
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, the event already finished.",
                ).set_footer(text="maybe next week!")
            )
            return

        await interaction.user.remove_roles(black_list_role)

        current_week["claimed_by"] = interaction.user.id
        user.sub_coins(current_week["amout"], "blacklist out")
        open_file("data/blacklist.json", weeks)

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                description=f"{interaction.user.mention}, congarts;\nYou get your freedom!",
            ),
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Blacklist(bot))
