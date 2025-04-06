import os
from datetime import UTC, date, datetime, timedelta
from typing import Literal

import discord

from config import get_users, get_config, get_cooldown, get_emoji, get_extension
from consts import BOT_COINS_AMOUNT, COLOR, EXCLUDE_DIRS, GOLDEN_RATIO
from models import UserData
from utils import convert_seconds, number


class SelfEmbeds:
    @staticmethod
    def stats(
        bot,
        duration: Literal[
            "last_24_hours", "last_7_days", "last_30_days", "last_year", "all_time"
        ],
    ) -> discord.Embed:
        factor, daily_factor = {
            "all_time": (
                30 * 24 * 3600,
                (datetime.now(UTC).date() - date(year=2023, month=7, day=24)).days,
            ),
            "last_year": (24 * 3600, 365),
            "last_30_days": (3600, 30),
            "last_7_days": (60, 7),
            "last_24_hours": (1, 1),
        }[duration]

        extension_count = {}
        total_count = 0
        for _, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file in files:
                extension = get_extension(file.split(".")[-1])
                extension_count.setdefault(extension, 0)
                extension_count[extension] += 1
                total_count += 1

        embed = (
            discord.Embed(
                color=COLOR.yellow,
                description=(
                    f"**Total**: {convert_seconds(int(total_count * factor * GOLDEN_RATIO))}\n"
                    f"**Daily Average**: {convert_seconds(int((total_count * factor * GOLDEN_RATIO) / daily_factor))}\n"
                    f"**Languages**:\n>>> "
                ),
            )
            .set_author(
                name=bot.user.name,
                icon_url=bot.user.avatar,
            )
            .set_footer(text=f"duration  -  {duration.replace('_', ' ')}")
        )

        max_lang_len = len(max(extension_count.keys(), key=len))

        for lang in sorted(extension_count.items(), key=lambda x: x[1], reverse=True):
            text = f"{get_emoji(lang[0])} {lang[0]:<{max_lang_len}} - {convert_seconds(int(lang[1] * factor * GOLDEN_RATIO))}"
            if len(embed.description) + len(text) > 4096:
                break
            embed.description += f"{text}\n"

        return embed

    @staticmethod
    def profile(bot) -> discord.Embed:
        return (
            discord.Embed(
                color=COLOR.yellow,
            )
            .set_author(name=bot.user.name, icon_url=bot.user.avatar)
            .add_field(
                name="Class",
                value=f"> **Coding** - Discord Integration",
                inline=False,
            )
            .add_field(
                name="Coins",
                value=f"> {number(BOT_COINS_AMOUNT)} {get_emoji("coin")}",
                inline=False,
            )
            .add_field(
                name="Favorite Language",
                value=f"> {get_emoji("Python")}  Python",
                inline=False,
            )
            .add_field(
                name="Socials",
                value=(
                    f"- [{get_emoji("github")}  github]({get_config("REPOSITORY")})\n"
                    f"- [{get_emoji("portfolio")}  portfolio](https://lionsgeek.ma/)"
                ),
            )
        )


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
        admins = get_users("admins")
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
        if (interaction.user.id in get_users("admins")) or (
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

    async def user_is_self(
        self,
        interaction: discord.Interaction,
        member: discord.User | discord.Member,
        **kwargs,
    ) -> bool:
        if self.user.id != member.id:
            return False
        match interaction.command.qualified_name:
            case "profile":
                await interaction.followup.send(
                    embed=SelfEmbeds.profile(self),
                )
            case "stats":
                await interaction.followup.send(
                    embed=SelfEmbeds.stats(self, kwargs.get("duration", "all_time")),
                )

        return True
