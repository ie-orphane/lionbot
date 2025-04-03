import discord
from typing import Literal
from datetime import datetime, UTC, timedelta
from cogs import Cog
from config import get_emoji
from api import wakapi


class Stats(Cog):
    @discord.app_commands.guild_only()
    @discord.app_commands.command(description="Show the coding stats.")
    @discord.app_commands.describe(
        duration="Choose a duration.", member="Choose a fellow geek."
    )
    async def stats(
        self,
        interaction: discord.Interaction,
        member: discord.Member | discord.User = None,
        duration: Literal[
            "last 24 hours", "last 7 days", "last 30 days", "last year", "all time"
        ] = "all time",
    ):
        await interaction.response.defer()
        self.cog_interaction(interaction, duration=duration, member=member)

        duration = duration.replace(" ", "_")

        member = member or interaction.user

        if (
            await self.bot.user_is_self(interaction, member, duration=duration)
            or await self.bot.user_on_cooldown(
                interaction, interaction.command.qualified_name
            )
            or (await self.bot.user_is_admin(interaction, member))
            or (user := await self.bot.user_is_unkown(interaction, member)) is None
        ):
            return

        if user.token is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{member.mention}, can't found your wakatime API KEY!",
                ),
                ephemeral=True,
            )
            return

        if ((user_data := await wakapi.get_current(user.token)) is None) or (
            (user_data := user_data.get("data")) is None
        ):
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{member.mention}, failed to get your data!",
                ),
                ephemeral=True,
            )
            return

        if duration == "last_24_hours":
            if (
                user_stats := await wakapi.get_summary(
                    user.token,
                    start=str((datetime.now(UTC) - timedelta(days=1)).date()),
                    end=str(datetime.now(UTC).date()),
                )
            ) is None:
                await interaction.followup.send(
                    embed=discord.Embed(
                        color=self.color.red,
                        description=f"{member.mention}, failed to get your stats!",
                    ),
                    ephemeral=True,
                )
                return

            daily_average = user_stats["daily_average"]["text"]
            total = user_stats["cumulative_total"]["text"]
            duration = "today"
            langs = user_stats["data"][0]["languages"]

        else:
            if (
                (user_stats := await wakapi.get_stats(user.token, duration)) is None
            ) or ((user_stats := user_stats.get("data")) is None):
                await interaction.followup.send(
                    embed=discord.Embed(
                        color=self.color.red,
                        description=f"{member.mention}, failed to get your stats!",
                    ),
                    ephemeral=True,
                )
                return

            daily_average = user_stats.get("human_readable_daily_average", -1)
            total = user_stats.get("human_readable_total", -1)
            duration = user_stats.get(
                "human_readable_range", duration.replace("_", " ")
            )
            langs = user_stats.get("languages", [])

        embed = (
            discord.Embed(
                color=self.color.yellow,
                description=f"**Total**: {total}\n**Daily Average**: {daily_average}",
            )
            .set_author(
                name=user.name,
                icon_url=member.display_avatar,
                url=user_data.get("profile_url"),
            )
            .set_footer(text=f"duration  -  {duration}")
        )

        languages = {
            lang["name"]: lang["text"]
            for lang in langs
            if lang["name"] != "Other"
            if lang["total_seconds"] >= 60
        }

        languages = "\n".join(
            [
                (
                    f"{get_emoji(lang)}"
                    f"{lang:^{sorted(map(lambda x: len(x), languages.keys()))[-1] + 2}}-"
                    f"{amount:^{sorted(map(lambda x: len(x), languages.values()))[-1] + 2}}"
                )
                for lang, amount in languages.items()
            ]
        )

        if len(languages) > 0:
            embed.description += f"\n**Languages**:\n>>> {languages}"

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Stats(bot))
