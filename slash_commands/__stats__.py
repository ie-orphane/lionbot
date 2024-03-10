import discord
from discord.ext import commands
from help import *
from datetime import datetime, UTC

class stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="stats", description="Show your WakaTime stats")
    @discord.app_commands.describe(
        duration="Choose a duration", member="Choose a member"
    )
    @discord.app_commands.choices(
        duration=[
            discord.app_commands.Choice(name=name, value=value)
            for name, value in {
                ("daily", ""),
                ("weekly", "last_7_days"),
                ("monthly", "last_30_days"),
                ("yearly", "last_year"),
                ("all time", "all_time"),
            }
        ]
    )
    async def stats_command(
        self,
        interaction: discord.Interaction,
        member: discord.Member = None,
        duration: str = "",
    ):
        member = member or interaction.user
        user_id = member.id
        user = get_data(user_id)

        # user not registered yet
        if not user:
            if member == interaction.user:
                txt = ", you are"
            else:
                txt = " is"
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=red,
                    description=f"{member.mention}{txt} not registered yet!",
                    ephemeral=True,
                )
            )
            return

        # user not verified
        if not user.verified:
            if member == interaction.user:
                txt = ", you are"
            else:
                txt = " is"
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=red, description=f"{member.mention}{txt} not verified yet!"
                )
            )
            return

        await interaction.response.defer()

        user_data = user.session.get("users/current").json()["data"]

        if duration == "":
            current_day = datetime.now(UTC).date()
            params = {"start": current_day, "end": current_day}
            user_stats = user.session.get(
                "users/current/summaries", params=params
            ).json()
            daily_average = user_stats["daily_average"]["text"]
            total = user_stats["cumulative_total"]["text"]
            duration = "today"
            langs = user_stats["data"][0]["languages"]

        else:
            user_stats = user.session.get(f"users/current/stats/{duration}").json()[
                "data"
            ]
            daily_average = user_stats["human_readable_daily_average"]
            total = user_stats["human_readable_total"]
            duration = user_stats["human_readable_range"]
            langs = user_stats["languages"]

        languages = []
        for index, lang in enumerate(langs):
            bold = "**" if index < 3 else ""

            if lang["minutes"] != 0:
                logo = const.emojis.get(lang["name"], "")
                languages.append(f"{logo}{bold}{lang['name']}{bold}  -  {lang['text']}")

            if lang["name"] == "Other":
                break
        languages = "\n".join(languages)

        statsEmbed = discord.Embed(
            color=yellow,
            description=f"### **total**:\n> {total}\n### **Daily avarage:** \n> {daily_average}\n\n### **Languages:**\n>>> {languages}",
        )
        statsEmbed.set_author(
            name=user_data["display_name"],
            icon_url=user_data["photo"],
            url=user_data["profile_url"],
        )
        statsEmbed.set_footer(text=f"duration  -  {duration}")
        await interaction.followup.send(embed=statsEmbed)


async def setup(bot: commands.Bot):
    await bot.add_cog(stats(bot))
