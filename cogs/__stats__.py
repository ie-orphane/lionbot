import os
import discord
import requests
from typing import Literal
from datetime import datetime, UTC, timedelta, date
from models import UserData
from cogs import Cog
from bot.config import Emoji
from constants import EXCLUDE_DIRS, GOLDEN_RATIO
from utils import convert_seconds


class Stats(Cog):
    @discord.app_commands.guild_only()
    @discord.app_commands.command(description="Show your WakaTime stats")
    @discord.app_commands.describe(
        duration="Choose a duration", member="Choose a member"
    )
    async def stats(
        self,
        interaction: discord.Interaction,
        member: discord.Member = None,
        duration: Literal[
            "last 24 hours", "last 7 days", "last 30 days", "last year", "all time"
        ] = "last 24 hours",
    ):
        await interaction.response.defer()
        duration = duration.replace(" ", "_")

        member = member or interaction.user

        if interaction.application_id == member.id:
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
                    extension = file.split(".")[-1]
                    extension = Emoji.extensions.get(extension, extension)
                    extension_count.setdefault(extension, 0)
                    extension_count[extension] += 1
                    total_count += 1

            max_lang_len = len(max(extension_count.keys(), key=len))

            languages = "\n".join(
                map(
                    lambda x: f"{Emoji.languages.get(x[0], " ")} {x[0]:<{max_lang_len}} - {convert_seconds(int(x[1] * factor * GOLDEN_RATIO))}",
                    sorted(extension_count.items(), key=lambda x: x[1], reverse=True),
                )
            )

            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.yellow,
                    description=(
                        f"**Total**: {convert_seconds(int(total_count * factor * GOLDEN_RATIO))}\n"
                        f"**Daily Average**: {convert_seconds(int((total_count * factor * GOLDEN_RATIO) / daily_factor))}\n"
                        f"**Languages**:\n>>> {languages}"
                    ),
                )
                .set_author(
                    name=member.name,
                    icon_url=member.avatar,
                )
                .set_footer(text=f"duration  -  {duration}")
            )
            return
        user = UserData.read(member.id)

        if user is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{member.mention}{', you are' if member == interaction.user  else ' is'} not registered yet!",
                ),
                ephemeral=True,
            )
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

        headers = {
            "Authorization": f"Basic {user.token}",
            "Content-Type": "application/json",
        }

        response = requests.get(
            url="https://wakatime.com/api/v1/users/current", headers=headers
        )

        if not response.ok:
            print(f"Error {response.status_code} : {response.text}")
            return

        user_data = response.json()["data"]

        if duration == "last_24_hours":
            response = requests.get(
                url="https://wakatime.com/api/v1/users/current/summaries",
                params={
                    "start": (datetime.now(UTC) - timedelta(days=1)).date(),
                    "end": datetime.now(UTC).date(),
                },
                headers=headers,
            )

            if not response.ok:
                print(f"Error {response.status_code} : {response.text}")
                return

            user_stats = response.json()
            daily_average = user_stats["daily_average"]["text"]
            total = user_stats["cumulative_total"]["text"]
            duration = "today"
            langs = user_stats["data"][0]["languages"]

        else:
            response = requests.get(
                url=f"https://wakatime.com/api/v1/users/current/stats/{duration}",
                headers=headers,
            )

            if not response.ok:
                print(f"Error {response.status_code} : {response.text}")
                return

            user_stats = response.json()["data"]
            daily_average = user_stats["human_readable_daily_average"]
            total = user_stats["human_readable_total"]
            duration = user_stats["human_readable_range"]
            langs = user_stats["languages"]

        languages = {
            lang["name"]: lang["text"]
            for lang in langs
            if lang["name"] != "Other"
            if lang["total_seconds"] >= 60
        }

        languages = "\n".join(
            [
                (
                    f"{Emoji.languages.get(lang, " ")}"
                    f"{lang:^{sorted(map(lambda x: len(x), languages.keys()))[-1] + 2}}-"
                    f"{amount:^{sorted(map(lambda x: len(x), languages.values()))[-1] + 2}}"
                )
                for lang, amount in languages.items()
            ]
        )

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.yellow,
                description=f"**Total**: {total}\n**Daily Average**: {daily_average}\n**Languages**:\n>>> {languages}",
            )
            .set_author(
                name=user_data["display_name"],
                icon_url=user_data["photo"],
                url=user_data["profile_url"],
            )
            .set_footer(text=f"duration  -  {duration}")
        )


async def setup(bot):
    await bot.add_cog(Stats(bot))
