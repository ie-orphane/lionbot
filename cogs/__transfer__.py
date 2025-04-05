import discord
from config import get_emoji
from cogs import Cog
from utils import number


class Transfer(Cog):
    @discord.app_commands.guild_only()
    @discord.app_commands.command(description="Send coins to your fellow geek.")
    @discord.app_commands.describe(amount="Choose an amount.", member="Choose a geek.")
    async def transfer(
        self,
        interaction: discord.Interaction,
        amount: discord.app_commands.Range[int, 1],
        member: discord.Member,
    ):
        await interaction.response.defer()
        self.cog_interaction(interaction, amount=amount, member=member)

        if member == interaction.user:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    title="❌ Transaction denied!",
                    description=(
                        f"✋ {interaction.user.mention},\n"
                        f"you can't transfer coins to yourself!"
                    ),
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
                    title="❌ Transaction denied!",
                    description=(
                        f"✋ {interaction.user.mention},\n"
                        f"you don't have {number(amount)} {get_emoji("coin")}!"
                        f"\nYour current balance is {number(user.coins)} {get_emoji("coin")}."
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
                title="✅ Transaction completed!",
                description=(
                    f"`Amount`: {number(amount)} {get_emoji("coin")}\n"
                    f"`Sender`: {interaction.user.mention}\n"
                    f"`Recipient`: {member.mention}"
                ),
            ),
        )


async def setup(bot):
    await bot.add_cog(Transfer(bot))
