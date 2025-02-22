import discord
from cogs import Cog
from models import UserData, UserLedger
from config import get_users, get_config


class Ledger(Cog):
    @discord.app_commands.guild_only()
    @discord.app_commands.command(description="show your transactions history.")
    @discord.app_commands.describe(member="choose a fellow member.")
    async def ledger(
        self,
        interaction: discord.Interaction,
        member: discord.Member | discord.User = None,
    ):
        await interaction.response.defer()

        member = member or interaction.user

        admins = get_users("owner", "coach", nullable=False)
        roles: set[discord.Role] = set()
        if not ((main_guild := self.bot.get_guild(get_config("GUILD"))) is None):
            roles = {
                role for role in main_guild.roles if role.name in get_config("ROLES")
            }
        if interaction.user != member and not (
            {role for role in interaction.user.roles} & roles
            or interaction.user.id in admins
        ):
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=(
                        f"{interaction.user.mention}, oops 🫣!\n"
                        f"You can't see {member.mention}'s profile.\n\n"
                        f"Only the following members can see other profiles:\n"
                        + "\n".join(
                            [
                                f"- {admin.mention}"
                                for admin in map(lambda x: self.bot.get_user(x), admins)
                                if admin
                            ]
                            + [f"- {role.mention}" for role in roles]
                        )
                    ),
                ),
                ephemeral=True,
            )
            return

        if (user := UserData.read(member.id)) is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{member.mention}{', you are' if member == interaction.user else ' is'} not registered yet!",
                ).set_footer(text="use /register instead"),
                ephemeral=True,
            )
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
                        for transaction in transactions
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
