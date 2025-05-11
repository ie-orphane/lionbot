from typing import Any, Coroutine

import discord

from cogs import GroupCog
from config import get_emoji
from consts import COLOR, GOLDEN_RATIO
from utils import is_float, number


async def _error(
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
            color=COLOR.red,
            title="❌ Operation failed!",
            description=f"✋ {interaction.user.mention},\n" + "\n".join(desc),
        ),
        ephemeral=True,
    )


@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
class Coins(GroupCog, name="coins"):
    @discord.app_commands.command(description="Add an amount of coins to a user 💰.")
    @discord.app_commands.describe(
        member="The user to reward.",
        reason="The reason for the addition ❓.",
        _expression="An amount of coins 💵.",
    )
    @discord.app_commands.rename(_expression="amount")
    async def add(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: discord.app_commands.Range[str, 3, 32],
        _expression: str,
    ):
        await interaction.response.defer()
        self.cog_interaction(
            interaction, member=member, expression=_expression, reason=reason
        )

        if (
            user := await self.bot.user_is_unkown(
                interaction, member, title="❌ Operation failed!"
            )
        ) is None:
            return

        options = {"GOLDEN_RATIO": GOLDEN_RATIO}
        try:
            expression = _expression.format(**options)
        except KeyError as e:
            await _error(interaction, f"**{e}** is an invalid key in `{_expression}`.")
            return
        try:
            amount = float(eval(expression))
        except Exception:
            await _error(
                interaction,
                f"Invalid syntax in `{_expression}`.",
                "\nexample of valid expression:",
                "`{GOLDEN_RATIO} * 11`.",
            )
            return

        if amount <= 0:
            await _error(
                interaction,
                f"`Amount` ({number(amount)}) must be greater than 0.",
            )
            return

        user.add_coins(amount, reason)

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                title="✅ Operation succeeded!",
                description=(
                    f"Amount: +{number(amount)} {get_emoji("coin")}\nHolder: {member.mention}\nReason: **`{reason}`**"
                    + (
                        ""
                        if is_float(_expression)
                        else f"\nExpression: **`{_expression}`** (`{expression}`)"
                    )
                ),
            )
        )

    @discord.app_commands.command(
        description="Subtracts an amount of coins from a user 💸."
    )
    @discord.app_commands.describe(
        member="The user to deduct coins from.",
        reason="The reason for the deduction.",
        _expression="An amount of coins 💰.",
    )
    @discord.app_commands.rename(_expression="amount")
    async def sub(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: discord.app_commands.Range[str, 3, 32],
        _expression: str,
    ):
        await interaction.response.defer()
        self.cog_interaction(
            interaction, member=member, expression=_expression, reason=reason
        )

        if (
            user := await self.bot.user_is_unkown(
                interaction, member, title="❌ Operation failed!"
            )
        ) is None:
            return

        options = {"GOLDEN_RATIO": GOLDEN_RATIO}
        try:
            expression = _expression.format(**options)
        except KeyError as e:
            await _error(interaction, f"**{e}** is an invalid key in `{_expression}`.")
            return
        try:
            amount = float(eval(expression))
        except Exception:
            await _error(
                interaction,
                f"Invalid syntax in `{_expression}`.",
                "\nexample of valid expression:",
                "`{GOLDEN_RATIO} * 11`.",
            )
            return

        if amount <= 0:
            await _error(
                interaction,
                f"`Amount` ({number(amount)}) must be greater than 0.",
            )
            return

        user.sub_coins(amount, reason)

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                title="✅ Operation succeeded!",
                description=(
                    f"Amount: -{number(amount)} {get_emoji("coin")}\nHolder: {member.mention}\nReason: **`{reason}`**"
                    + (
                        ""
                        if is_float(_expression)
                        else f"\nExpression: **`{_expression}`** (`{expression}`)"
                    )
                ),
            )
        )


async def setup(bot):
    await bot.add_cog(Coins(bot))
