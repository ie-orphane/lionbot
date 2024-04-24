import discord
from discord.ext import commands
from models import UserData
from utils import dclr


class Transfer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="transfer", description="transfer coins to anthor geek"
    )
    @discord.app_commands.describe(amount="choose an amount", member="choose a geek")
    async def transfer_command(
        self, interaction: discord.Interaction, amount: int, member: discord.Member
    ):
        await interaction.response.defer()

        if member == interaction.user:
            await interaction.followup.send(
                embed=discord.Embed(
                    title=f"transfer denied",
                    color=dclr.red,
                    description=f"{interaction.user.mention}, you can't transfer coins to yourself!",
                ),
                ephemeral=True,
            )
            return

        user_data = UserData.read(interaction.user.id)
        recipient_data = UserData.read(member.id)

        # user not registered yet
        if user_data is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=dclr.red,
                    description=f"{interaction.user.mention}, you are not registered yet!",
                ),
                ephemeral=True,
            )
            return

        if recipient_data is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=dclr.red,
                    description=f"{member.mention} is not registered yet!",
                ),
                ephemeral=True,
            )
            return

        if amount > user_data.coins:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=dclr.red,
                    description=(
                        f"{member.mention}, you don't have {amount} {self.bot.coin}!"
                        f"\nYour current balance is {user_data.coins} {self.bot.coin}."
                    ),
                ),
                ephemeral=True,
            )
            return

        # +- coins
        user_data.coins -= amount
        recipient_data.coins += amount

        # update data
        user_data.update()
        recipient_data.update()

        await interaction.followup.send(embed=discord.Embed(
            color=dclr.yellow,
            description=f"{amount} {self.bot.coin} transfered from {interaction.user.mention} to {member.mention}.",
        ))


async def setup(bot: commands.Bot):
    await bot.add_cog(Transfer(bot))
