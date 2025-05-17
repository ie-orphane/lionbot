from typing import Any, Coroutine

import discord

from cogs import Cog
from config import bot, get_emoji
from consts import MESSAGE, TRANSACTION_FEE
from utils import number


class Transfer(Cog):
    async def __error(
        self, interaction: discord.Interaction, *desc: tuple[str]
    ) -> Coroutine[Any, Any, None]:
        """
        Send an error interaction to the user.
        Args:
            interaction (discord.Interaction): The interaction containing the command.
            desc (tuple[str]): The error description.
        """
        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.red,
                title="❌ Transaction denied!",
                description=f"✋ {interaction.user.mention},\n" + "\n".join(desc),
            ),
            ephemeral=True,
        )

    @discord.app_commands.guild_only()
    @discord.app_commands.command(description="Send coins to your fellow geek.")
    @discord.app_commands.describe(amount="Choose an amount.", geek="Choose a geek.")
    async def transfer(
        self,
        interaction: discord.Interaction,
        amount: discord.app_commands.Range[int, 1],
        geek: discord.Member,
    ):
        """
        Transfer coins to another geek.
        Args:
            interaction (discord.Interaction): The interaction containing the command.
            amount (discord.app_commands.Range[int, 1]): The amount of coins to transfer.
            geek (discord.Member): The user to transfer coins to.
        """
        await interaction.response.defer()
        self.cog_interaction(interaction, amount=amount, geek=geek)

        if geek == interaction.user:
            return await self.__error(
                interaction,
                "you can't transfer coins to yourself!",
            )

        if (
            user := await self.bot.user_is_unkown(
                interaction, title="❌ Transaction denied!"
            )
        ) is None:
            return

        if geek == self.bot.user:
            if amount > user.coins:
                return await self.__error(
                    interaction,
                    f"you don't have {number(amount)} {get_emoji('coin')}!",
                    f"Your current balance is {number(user.coins)} {get_emoji('coin')}.",
                )

            bot.coins += amount
            user.sub_coins(amount, "donation")

            return await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.yellow,
                    title="✅ Donation completed!",
                    description=(
                        f"`Amount`: {number(amount)} {get_emoji("coin")}\n"
                        f"`Donator`: {interaction.user.mention}\n"
                    ),
                ).set_footer(text=MESSAGE.donation),
            )

        if (amount + amount * TRANSACTION_FEE) > user.coins:
            return await self.__error(
                interaction,
                f"you don't have {number(amount)} {get_emoji('coin')}!",
                f"Your current balance is {number(user.coins)} {get_emoji('coin')}.",
            )

        if (
            recipient := await self.bot.user_is_unkown(
                interaction, geek, title="❌ Transaction denied!"
            )
        ) is None:
            return

        user.sub_coins(amount, "transfer")
        user.sub_coins(amount * TRANSACTION_FEE, "fee")
        recipient.add_coins(amount, "transfer")
        bot.coins += amount * TRANSACTION_FEE

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.yellow,
                title="✅ Transaction completed!",
                description=(
                    f"`Amount`: {number(amount)} {get_emoji("coin")}\n"
                    f"`Fee`: {number(amount*TRANSACTION_FEE)} {get_emoji("coin")}\n"
                    f"`Sender`: {interaction.user.mention}\n"
                    f"`Recipient`: {geek.mention}"
                ),
            ),
        )


async def setup(bot):
    await bot.add_cog(Transfer(bot))
