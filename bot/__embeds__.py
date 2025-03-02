import discord
from models import UserData
from consts import COLOR
from config import get_config, get_users, get_cooldown
from datetime import datetime, timedelta, UTC


class BotEmbeds:
    @staticmethod
    async def user_is_unkown(
        interaction: discord.Interaction,
        member: discord.Member | discord.User = None,
        /,
        **kwargs,
    ) -> UserData | None:
        member = member or interaction.user
        if (user := UserData.read(member.id)) is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    **kwargs,
                    color=COLOR.red,
                    description=(
                        f"✋ {interaction.user.mention}, \n"
                        + (
                            f"you need to register before using the `/{interaction.command.qualified_name}`.\n"
                            + "Instead, use the `/register` command."
                        )
                        if member == interaction.user
                        else f"✋ {member.mention} is not registered yet!"
                    ),
                ),
                ephemeral=True,
            )
            return
        return user

    async def user_is_admin(
        self,
        interaction: discord.Interaction,
        member: discord.Member | discord.User,
    ) -> bool:
        admins = get_users("owner", "coach", nullable=False)
        roles: set[discord.Role] = set()
        if not ((main_guild := self.get_guild(get_config("GUILD"))) is None):
            roles = {
                role for role in main_guild.roles if role.name in get_config("ROLES")
            }
        if interaction.user != member and not (
            {role for role in interaction.user.roles} & roles
            or interaction.user.id in admins
        ):
            await interaction.followup.send(
                embed=discord.Embed(
                    color=COLOR.red,
                    description=(
                        f"{interaction.user.mention}, oops 🫣!\n"
                        f"You can't see {member.mention}'s {interaction.command.qualified_name}.\n\n"
                        f"Only the following members can see other profiles:\n"
                        + "\n".join(
                            [
                                f"- {admin.mention}"
                                for admin in map(lambda x: self.get_user(x), admins)
                                if admin
                            ]
                            + [f"- {role.mention}" for role in roles]
                        )
                    ),
                ),
                ephemeral=True,
            )
            return True
        return False

    @staticmethod
    async def user_on_cooldown(interaction: discord.Interaction, label: str) -> bool:
        if (interaction.user.id in get_users("owner", "coach", nullable=False)) or (
            (user := UserData.read(interaction.user.id)) is None
        ):
            return False

        if user.cooldowns is None:
            user.cooldowns = {}

        if user.cooldowns.get(label) is None:
            user.cooldowns[label] = str(datetime.now(UTC))
            user.update()
            return False

        available_time = datetime.fromisoformat(user.cooldowns[label]) + timedelta(
            seconds=get_cooldown(label)
        )

        if available_time < datetime.now(UTC):
            user.cooldowns[label] = str(datetime.now(UTC))
            user.update()
            return False

        await interaction.followup.send(
            embed=discord.Embed(
                color=COLOR.red,
                description=(
                    f"{interaction.user.mention}, ⏰\n"
                    f"You are on cooldown for this command!\n"
                    f"Next available in <t:{int(available_time.timestamp())}:T>."
                ),
            )
        )

        return True
