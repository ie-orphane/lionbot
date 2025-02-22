import discord
import datetime as dt
from discord.ext import commands
from utils import open_file, get_week
from config import get_emoji
from consts import OUTLIST_AMOUNT
from utils import number
from cogs import GroupCog


@discord.app_commands.guild_only()
class Blacklist(GroupCog, name="blacklist"):
    @discord.app_commands.command(
        description="A way for escaping from the blacklist ⛓."
    )
    async def out(self, interaction: discord.Interaction):
        await interaction.response.defer()

        if (user := await self.bot.user_is_unkown(interaction)) is None:
            return

        black_list_role = None

        for role in interaction.guild.roles:
            if role.name == "Black List":
                black_list_role = role

        amount = OUTLIST_AMOUNT

        if (
            black_list_role is None
            or interaction.user.get_role(black_list_role.id) is None
        ):
            if user.greylist:
                await interaction.user.add_roles(black_list_role)
                user.greylist = False
                user.update()
                await interaction.followup.send(
                    embed=discord.Embed(
                        color=self.color.yellow,
                        description=(
                            f"{interaction.user.mention}, congrats for joining **BlackList**.\n"
                            f"To appeal 😔, you must pay {number(amount)} {get_emoji('coin')}."
                        ),
                    )
                )
                return

            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, next time maybe 🤔.\nWe can't find you in blacklist.",
                ).set_footer(text="wanna join it?")
            )
            user.greylist = True
            user.update()
            return

        this_week = get_week()
        weeks = open_file("data/outlist.json")
        current_week = weeks.get(str(this_week.count))

        if (
            not (current_week is None)
            and (current_week["claimed_by"] is None)
            and dt.datetime.fromisoformat(current_week["started_at"])
            <= dt.datetime.now(dt.UTC).replace(second=0, microsecond=0)
            <= dt.datetime.fromisoformat(current_week["started_at"])
            + dt.timedelta(seconds=current_week["ends_in"])
        ):
            amount = current_week["amout"]

        if user.coins < amount:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, you need {number(amount - user.coins)} {get_emoji("coin")} more.",
                )
            )
            return

        await interaction.user.remove_roles(black_list_role)

        if amount != OUTLIST_AMOUNT:
            current_week["claimed_by"] = interaction.user.id
            open_file("data/outlist.json", weeks)

        user.greylist = False
        user.sub_coins(amount, "blacklist out")

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                description=f"{interaction.user.mention}, congarts 🥳!\nYou paied {number(amount)} {get_emoji("coin")}",
            ).set_footer(text="you're free now."),
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Blacklist(bot))
