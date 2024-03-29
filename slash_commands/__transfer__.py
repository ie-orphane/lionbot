import discord
from discord.ext import commands
from models import UserData
from utils import color
from models import LedgerData
from datetime import datetime, UTC


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
        if member == interaction.user:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"transfer denied",
                    color=color.red,
                    description=f"{interaction.user.mention}, you can't transfer coins to yourself!",
                ),
                ephemeral=True,
            )
            return

        user_data = UserData.read(interaction.user.id)
        recipient_data = UserData.read(member.id)

        # user not registered yet
        if user_data is None:
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=color.red,
                    description=f"{interaction.user.mention}, you are not registered yet!",
                ),
                ephemeral=True,
            )
            return

        if recipient_data is None:
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=color.red,
                    description=f"{member.mention} is not registered yet!",
                ),
                ephemeral=True,
            )
            return

        if amount > user_data.coins:
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=color.red,
                    description=(
                        f"{member.mention}, you don't have {amount} <:lioncoin:1219417317419651173>!"
                        f"\nYour current balance is {user_data.coins} <:lioncoin:1219417317419651173>."
                    ),
                ),
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        # +- coins
        user_data.coins -= amount
        recipient_data.coins += amount

        # update activity
        user_data.ledger.append(
            LedgerData(
                moment=str(datetime.now(UTC)),
                type="send",
                amount=amount,
            )
        )

        recipient_data.ledger.append(
            LedgerData(
                moment=str(datetime.now(UTC)),
                type="receive",
                amount=amount,
            )
        )

        # update data
        user_data.update()
        recipient_data.update()

        transferEmbed = discord.Embed(
            color=color.yellow,
            description=f"{amount} <:lioncoin:1219417317419651173> transfered from {interaction.user.mention} to {member.mention}.",
        )

        await interaction.followup.send(embed=transferEmbed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Transfer(bot))
