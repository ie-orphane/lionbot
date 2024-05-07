import discord
import requests
from typing import Literal
from datetime import datetime, UTC, timedelta
from models import UserData
from cogs import Cog
from bot.config import Emoji


class Stats(Cog):
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
                params={
                    "start": (datetime.now(UTC) - timedelta(days=1)).date(),
                    "end": datetime.now(UTC).date(),
                },
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

        languages = []
        for index, lang in enumerate(langs):
            bold = "**" if index < 3 else ""

            if lang["minutes"] != 0:
                logo = Emoji.languages.get(lang["name"], "")
                languages.append(f"{logo}{bold}{lang['name']}{bold}  -  {lang['text']}")

            if lang["name"] == "Other":
                break
        languages = "\n".join(languages)

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.yellow,
                description=f"### total:\n> {total}\n### Daily avarage:\n> {daily_average}\n\n### Languages:\n>>> {languages}",
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
