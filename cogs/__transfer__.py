import discord
from models import UserData
from config import get_emoji
from cogs import Cog


class Transfer(Cog):
    @discord.app_commands.guild_only()
    @discord.app_commands.command(description="transfer coins to anthor geek")
    @discord.app_commands.describe(amount="choose an amount", member="choose a geek")
    async def transfer(
        self, interaction: discord.Interaction, amount: int, member: discord.Member
    ):
        await interaction.response.defer()

        if amount <= 0:
            await interaction.followup.send(
                embed=discord.Embed(
                    title=f"transfer denied",
                    color=self.color.red,
                    description=f"{interaction.user.mention}, **{amount}** is an invalid amount!",
                ).set_footer(text="the minimum amount is 1."),
                ephemeral=True,
            )
            return

        if member == interaction.user:
            await interaction.followup.send(
                embed=discord.Embed(
                    title=f"transfer denied",
                    color=self.color.red,
                    description=f"{interaction.user.mention}, you can't transfer coins to yourself!",
                ),
                ephemeral=True,
            )
            return

        user_data = UserData.read(interaction.user.id)
        recipient_data = UserData.read(member.id)

        if user_data is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, you are not registered yet!",
                ),
                ephemeral=True,
            )
            return

        if recipient_data is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{member.mention} is not registered yet!",
                ),
                ephemeral=True,
            )
            return

        if amount > user_data.coins:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=(
                        f"{member.mention}, you don't have {amount} {get_emoji("coin")}!"
                        f"\nYour current balance is {user_data.coins} {get_emoji("coin")}."
                    ),
                ),
                ephemeral=True,
            )
            return

        user_data.sub_coins(amount, "transfer")
        recipient_data.add_coins(amount, "transfer")

        user_data.update()
        recipient_data.update()

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.yellow,
                description=f"{amount} {get_emoji("coin")} transfered from {interaction.user.mention} to {member.mention}.",
            )
        )


async def setup(bot):
    await bot.add_cog(Transfer(bot))
