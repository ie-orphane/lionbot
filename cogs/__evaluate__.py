from typing import Any, Coroutine

import discord

from cogs import Cog
from consts import GOLDEN_RATIO
from utils import number


class Evaluate(Cog):
    @staticmethod
    async def __error(
        interaction: discord.Interaction, *desc: tuple[str]
    ) -> Coroutine[Any, Any, None]:
        """
        Send an error message to the user.
        Args:
            message (discord.Message): The message containing the command.
            desc (tuple[str]): The error description.
        """
        await interaction.followup.send(
            embed=discord.Embed(
                color=Cog.color.red,
                description=f"✋ {interaction.user.mention},\n" + "\n".join(desc),
            ),
            ephemeral=True,
        )

    @discord.app_commands.command(description="Evaluate a coins amount expression.")
    @discord.app_commands.guild_only()
    @discord.app_commands.default_permissions(administrator=True)
    @discord.app_commands.describe(
        expression="The expression to evaluate. Use {GOLDEN_RATIO} for the golden ratio."
    )
    async def evaluate(self, interaction: discord.Interaction, expression: str):
        await interaction.response.defer(ephemeral=True)
        self.cog_interaction(interaction, expression=expression)

        options = {"GOLDEN_RATIO": GOLDEN_RATIO}
        try:
            _expression = expression.format(**options)
        except KeyError as e:
            await self.__error(
                interaction, f"**{e}** is an invalid key in `{expression}`."
            )
            return

        try:
            amount = float(eval(_expression))
        except Exception:
            await self.__error(
                interaction,
                f"Invalid syntax in `{expression}`.",
                "example of valid expression:",
                "`{GOLDEN_RATIO} * 11`.",
            )
            return

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                description=f"`{expression}` => `{_expression}` => {number(amount)}",
            ),
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(Evaluate(bot))
