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
    @discord.app_commands.choices(
        ledger=[
            discord.app_commands.Choice(name="True", value=1),
            discord.app_commands.Choice(name="False", value=0),
        ]
    )
    async def wallet_command(
        self,
        interaction: discord.Interaction,
        member: discord.Member | None = None,
        ledger: int = 0,
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

        txt = f"{member.mention}{', you balance is' if member == interaction.user else ' has a balance of'} **{user_data.coins}**"
        if ledger and member == interaction.user:
            txt += f"\n\n***ledger***\n{'\n'.join([ 
                    f"- {ledger:%m} {' '*3} **{ledger:%t}{ledger.amount}**" for ledger in user_data.ledger
                ])}"

        walletEmbed = discord.Embed(
            color=color.yellow,
            description=txt,
        )
        walletEmbed.set_author(name=user_data.name, icon_url=member.avatar)

        await interaction.followup.send(embed=walletEmbed)


async def setup(bot: commands.Bot):
    await bot.add_cog(wallet(bot))
