import discord
import requests
from models import UserData
from typing import Union
from bot.config import Emoji
from cogs import Cog
from constants import BOT_COINS_AMOUNT
from utils import number


class Profile(Cog):
    @discord.app_commands.guild_only()
    @discord.app_commands.command(description="view your profile")
    @discord.app_commands.describe(member="see member profile")
    async def profile(
        self,
        interaction: discord.Interaction,
        member: Union[discord.Member, discord.User] = None,
    ):
        await interaction.response.defer()

        member = member or interaction.user

        if interaction.application_id == member.id:
            embed = (
                discord.Embed(
                    color=self.color.yellow,
                )
                .set_author(name=member.name, icon_url=member.avatar)
                .add_field(
                    name="Class",
                    value=f"> **Coding** - Discord Integration",
                    inline=False,
                )
                .add_field(
                    name="Coins",
                    value=f"> **{'**.'.join(str(number(BOT_COINS_AMOUNT)).split('.')) if '.' in str(BOT_COINS_AMOUNT) else f'{number(BOT_COINS_AMOUNT)}**'} {Emoji.coin}",
                )
                .add_field(
                    name="Favorite Language",
                    value=f"> {Emoji.languages["Python"]} Python",
                    inline=False,
                )
                .add_field(
                    name="Socials",
                    value=(
                        f"- [{Emoji.get("github")}github](https://github.com/ie-orphane/lionbot)\n"
                        f"- [{Emoji.get("portfolio")}portfolio](https://lionsgeek.ma/)"
                    ),
                )
            )

            await interaction.followup.send(embed=embed)
            return

        user = UserData.read(member.id)

        if user is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{member.mention}{', you are' if member == interaction.user else ' is'} not registered yet!",
                )
            )
            return

        favorite_language = ""
        wakatime_url = ""

        if user.token:
            response = requests.get(
                url="https://wakatime.com/api/v1/users/current/stats/all_time",
                headers={
                    "Authorization": f"Basic {user.token}",
                    "Content-Type": "application/json",
                },
            )

            if response.ok:
                user_data = response.json()["data"]
                wakatime_url = f"https://wakatime.com/@{user_data['user_id']}"
                if languages := user_data["languages"]:
                    favorite_language = sorted(
                        languages, key=lambda x: x["total_seconds"]
                    )[-1]

        embed = discord.Embed(
            color=self.color.yellow,
        ).set_author(name=user.name, icon_url=member.avatar)

        if user.training and user.training.startswith("coding"):
            embed.add_field(
                name="Class",
                value=f"> **Coding** - Web Development **{user.training.removeprefix("coding")}**",
                inline=False,
            )

        embed.add_field(
            name="Coins",
            value=f"> **{'**.'.join(str(number(user.coins)).split('.')) if '.' in str(user.coins) else f'{number(user.coins)}**'} {Emoji.coin}",
        )

        if favorite_language:
            embed.add_field(
                name="Favorite Language",
                value=f"> {Emoji.languages[favorite_language['name']]} {favorite_language['name']}",
                inline=False,
            )

        user._socials["wakatime"] = wakatime_url
        embed.add_field(
            name="Socials",
            value="\n".join(
                [
                    f"- [{Emoji.get(social)}{social}]({link})"
                    for social, link in user.socials
                    if link
                ]
            ),
        )

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Profile(bot))
