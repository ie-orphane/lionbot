import discord
from cogs import GroupCog
from models import UserData
from utils import number
from config import get_emoji


@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
class Coins(GroupCog, name="coins"):
    @discord.app_commands.command(description="Add an amount of coins to a user 💰")
    @discord.app_commands.rename(_member="member")
    @discord.app_commands.describe(
        _member="The user to reward",
        amount="The amount of coins to add 💵",
        reason="The reason for the addition ❓",
    )
    async def add(
        self,
        interaction: discord.Interaction,
        _member: discord.Member,
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

        if (member := UserData.read(_member.id)) is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    title="❌ Operation failed!",
                    description=f"{_member.mention} is not registered yet.",
                ),
                ephemeral=True,
            )
            return

        member.add_coins(amount, reason)

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                title="✅ Operation succeeded!",
                description=f"Successfully added {number(amount)} {get_emoji("coin")} to {_member.mention}'s balance for the reason: `{reason}`.",
            )
        )

    @discord.app_commands.command(
        description="Subtracts an amount of coins from a user 💸"
    )
    @discord.app_commands.rename(_member="member")
    @discord.app_commands.describe(
        _member="The user to deduct coins from",
        amount="The amount of coins to subtract 💰",
        reason="The reason for the deduction",
    )
    async def sub(
        self,
        interaction: discord.Interaction,
        _member: discord.Member,
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

        if (member := UserData.read(_member.id)) is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    title="❌ Operation failed!",
                    description=f"{_member.mention} is not registered yet.",
                ),
                ephemeral=True,
            )
            return
        member.sub_coins(amount, reason)

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                title="✅ Operation succeeded!",
                description=f"Successfully subtracted {number(amount)} {get_emoji("coin")} from {_member.mention}'s balance for the reason: `{reason}`.",
            )
        )


async def setup(bot):
    await bot.add_cog(Coins(bot))
