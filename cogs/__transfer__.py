import discord
from config import get_emoji
from cogs import Cog


class Transfer(Cog):
    @discord.app_commands.guild_only()
    @discord.app_commands.command(description="Send coins to your fellow geek.")
    @discord.app_commands.describe(amount="Choose an amount.", member="Choose a geek.")
    async def transfer(
        self, interaction: discord.Interaction, amount: int, member: discord.Member
    ):
        await interaction.response.defer()

        if amount <= 0:
            await interaction.followup.send(
                embed=discord.Embed(
                    title="❌ Transaction denied!",
                    color=self.color.red,
                    description=f"{interaction.user.mention}, **{amount}** is an invalid amount!",
                ).set_footer(text="the minimum amount is 1."),
                ephemeral=True,
            )
            return

        if member == interaction.user:
            await interaction.followup.send(
                embed=discord.Embed(
                    title="❌ Transaction denied!",
                    color=self.color.red,
                    description=f"{interaction.user.mention}, you can't transfer coins to yourself!",
                ),
                ephemeral=True,
            )
            return

        if (
            user := await self.bot.user_is_unkown(
                interaction, title="❌ Transaction denied!"
            )
        ) is None:
            return

        if (
            recipient := await self.bot.user_is_unkown(
                interaction, member, title="❌ Transaction denied!"
            )
        ) is None:
            return

        if amount > user.coins:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=(
                        f"{member.mention}, you don't have {amount} {get_emoji("coin")}!"
                        f"\nYour current balance is {user.coins} {get_emoji("coin")}."
                    ),
                ),
                ephemeral=True,
            )
            return

        user.sub_coins(amount, "transfer")
        recipient.add_coins(amount, "transfer")

        user.update()
        recipient.update()

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.yellow,
                description=f"{amount} {get_emoji("coin")} transfered from {interaction.user.mention} to {member.mention}.",
            )
        )


async def setup(bot):
    await bot.add_cog(Transfer(bot))
