import discord
from cogs import Cog
from models import UserLedger


class Ledger(Cog):
    @discord.app_commands.guild_only()
    @discord.app_commands.command(description="Show your transactions history.")
    @discord.app_commands.describe(member="Choose a fellow geek.")
    async def ledger(
        self,
        interaction: discord.Interaction,
        member: discord.Member | discord.User = None,
    ):
        await interaction.response.defer(ephemeral=True)
        self.cog_interaction(interaction, member=member)

        member = member or interaction.user

        if (
            await self.bot.user_on_cooldown(interaction, interaction.command.qualified_name)
            or (await self.bot.user_is_admin(interaction, member))
            or (user := await self.bot.user_is_unkown(interaction, member)) is None
        ):
            return

        transactions = []
        max_int = tuple(map(len, str(float(user.coins)).split(".")))

        for transaction in UserLedger.get(user.id)[::-1]:
            max_int = (
                max(max_int[0], len(str(float(transaction.amount)).split(".")[0])),
                max(max_int[1], len(str(float(transaction.amount)).split(".")[1])),
            )
            transactions.append(transaction)
            if len(transactions) >= 11:
                break

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.blue,
                description=f"```ansi\n{'datetime':^14} {'amount':^{max_int[0] + max_int[1] + 2}} {'reason'}\n\n"
                + "\u001b[0;30m------------------------------------------------\u001b[0;0m\n"
                + "\n".join(
                    [
                        f"\u001b[0;30m{transaction.datetimezone:%d/%m/%y %H:%M}\u001b[0;0m "
                        f"{" " * (max_int[0] - len(str(float(transaction.amount)).split(".")[0]))}{transaction.op}{float(transaction.amount)}\u001b[0;0m{" " * (max_int[1] - len(str(float(transaction.amount)).split(".")[1]))}"
                        f" {transaction.reason}"
                        for transaction in transactions[::-1]
                    ]
                    + [
                        f"{" " * 15}\u001b[0;30m{'-' * (max_int[0] + max_int[1] + 2):>16}\u001b[0;0m\n{"current":^16}"
                        + f"{" " * (max_int[0] - len(str(float(user.coins)).split(".")[0]))}\u001b[0;34m{float(user.coins)}\u001b[0;0m"
                    ]
                )
                + "\n```",
            )
            .set_author(
                name=f"{member.display_name}' ledger",
                icon_url=member.display_avatar,
            )
            .set_footer(text=f"last {len(transactions)} balance transaction(s).")
        )


async def setup(bot):
    await bot.add_cog(Ledger(bot))
