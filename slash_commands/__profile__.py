import discord
from discord.ext import commands
from models import UserData, WeekData
from utils import color


class profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="profile", description="view your profile")
    @discord.app_commands.describe(member="see member profile")
    async def profile_command(
        self, interaction: discord.Interaction, member: discord.Member = None
    ):
        await interaction.response.defer()

        member = member or interaction.user
        user_data = UserData.read(member.id)

        # user not registered yet
        if user_data is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=color.red,
                    description=f"{member.mention}{', you are' if member == interaction.user else ' is'} not registered yet!",
                )
            )
            return

        languages = {}
        for week_data in WeekData.read_all():
            for geek in week_data.geeks:
                if geek.id == member.id:
                    for lang, amount in geek.languages.items():
                        if lang == "Other":
                            continue
                        try:
                            languages[lang] += amount
                        except KeyError:
                            languages[lang] = amount
        fav_language = [
            lang
            for lang, _ in sorted(languages.items(), key=lambda x: x[1], reverse=True)
        ][0]

        profile_embed = discord.Embed(
            color=color.blue,
            description=(
                f"class: Coding - Web Development II\nfavorite language: **{fav_language}**"
                f"\nsocials: [github]({user_data.github}) {'' if user_data.portfolio is None else f'[portfolio]({user_data.portfolio})'}"
            ),
        )
        profile_embed.set_author(name=user_data.name, icon_url=member.avatar)

        await interaction.followup.send(embed=profile_embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(profile(bot))
