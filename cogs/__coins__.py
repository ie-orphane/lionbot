import discord
from cogs import GroupCog
from utils import number
from config import get_emoji


@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
class Coins(GroupCog, name="coins"):
    @discord.app_commands.command(description="Add an amount of coins to a user 💰.")
    @discord.app_commands.describe(
        member="The user to reward.",
        amount="The amount of coins to add 💵.",
        reason="The reason for the addition ❓.",
    )
    async def add(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        amount: float,
        reason: str,
    ):
        await interaction.response.defer()
        self.cog_interaction(interaction, member=member, amount=amount, reason=reason)

        if amount <= 0:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    title="❌ Operation failed!",
                    description=f"**{amount}** is an invalid amount!",
                ).set_footer(text="the minimum amount is 0.xx."),
                ephemeral=True,
            )
            return

        if (
            user := await self.bot.user_is_unkown(
                interaction, member, title="❌ Operation failed!"
            )
        ) is None:
            return

        user.add_coins(amount, reason)

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                title="✅ Operation succeeded!",
                description=f"Opeartion: **Addition** (**+**)\nAmount: {number(amount)} {get_emoji("coin")}\nHolder: {member.mention}\nReason: **`{reason}`**",
            )
        )

    @discord.app_commands.command(
        description="Subtracts an amount of coins from a user 💸."
    )
    @discord.app_commands.describe(
        member="The user to deduct coins from.",
        amount="The amount of coins to subtract 💰.",
        reason="The reason for the deduction.",
    )
    async def sub(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        amount: float,
        reason: str,
    ):
        await interaction.response.defer()

        if amount <= 0:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    title="❌ Operation failed!",
                    description=f"**{amount}** is an invalid amount!",
                ).set_footer(text="the minimum amount is 0.xx."),
                ephemeral=True,
            )
            return

        if (
            user := await self.bot.user_is_unkown(
                interaction, member, title="❌ Operation failed!"
            )
        ) is None:
            return

        user.sub_coins(amount, reason)

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                title="✅ Operation succeeded!",
                description=f"Opeartion: **Substraction** (**-**)\nAmount: {number(amount)} {get_emoji("coin")}\nHolder: {member.mention}\nReason: **`{reason}`**",
            )
        )


async def setup(bot):
    await bot.add_cog(Coins(bot))
