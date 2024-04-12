import discord
from discord.ext import commands
from models import UserData
from utils import color


class wallet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="wallet", description="show your current balance"
    )
    @discord.app_commands.describe(
        ledger="show wallet ledger", member="choose a member"
    )
    async def wallet_command(
        self,
        interaction: discord.Interaction,
        member: discord.Member | None = None,
        ledger: bool = False,
    ):
        member = member or interaction.user
        user_data = UserData.read(member.id)

        # user not registered yet
        if user_data is None:
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=color.red,
                    description=f"{member.mention}{', you are' if member == interaction.user else ' is'} not registered yet!",
                )
            )
            return

        await interaction.response.defer()

        walletEmbed = discord.Embed(
            color=color.yellow,
            description=f"{member.mention}{', you balance is' if member == interaction.user else ' has a balance of'} **{user_data.coins}** <:lioncoin:1219417317419651173>",
        ).set_author(name=user_data.name, icon_url=member.avatar)

        if ledger and member == interaction.user:
            walletEmbed.add_field(
                name="ledger",
                value="\n".join(
                    [
                        f"{ledger:%d} {ledger:%m} **{ledger:%t}{ledger.amount}**"
                        for ledger in user_data.ledger
                    ]
                ),
            )

        await interaction.followup.send(embed=walletEmbed)


async def setup(bot: commands.Bot):
    await bot.add_cog(wallet(bot))
