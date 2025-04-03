import discord
from discord.ext import commands
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
        self.cog_interaction(interaction)

        if (user := await self.bot.user_is_unkown(interaction)) is None:
            return

        black_list_role = None

        for role in interaction.guild.roles:
            if role.name == "Black List":
                black_list_role = role

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
                            f"{interaction.user.mention}, congrats for joining {black_list_role.mention}.\n"
                            f"To appeal 😔, you must pay {number(OUTLIST_AMOUNT)} {get_emoji('coin')}."
                        ),
                    )
                )
                return

            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, next time maybe 🤔.\nWe can't find you in {black_list_role.mention}.",
                ).set_footer(text="wanna join it?")
            )
            user.greylist = True
            user.update()
            return

        if user.coins < OUTLIST_AMOUNT:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, you need {number(OUTLIST_AMOUNT - user.coins)} {get_emoji("coin")} more.",
                )
            )
            return

        await interaction.user.remove_roles(black_list_role)

        user.greylist = False
        user.sub_coins(OUTLIST_AMOUNT, "blacklist out")

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                description=f"{interaction.user.mention}, congarts 🥳!\nYou paied {number(OUTLIST_AMOUNT)} {get_emoji("coin")}.",
            ).set_footer(text="you're free now."),
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Blacklist(bot))
