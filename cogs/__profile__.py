import discord
from models import UserData
from typing import Union
import requests
from bot.config import Emoji
from cogs import Cog


class Profile(Cog):
    @discord.app_commands.command(description="view your profile")
    @discord.app_commands.describe(member="see member profile")
    async def profile(
        self,
        interaction: discord.Interaction,
        member: Union[discord.Member, discord.User] = None,
    ):
        await interaction.response.defer()

        member = member or interaction.user
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
                    favorite_language = sorted(languages, key=lambda x: x["total_seconds"])[-1]

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.yellow,
                description=(
                    f'{"### class:\n> **Coding** - Web Development **II**\n" if user.training == "codingII" else ""}'
                    f"### coins:\n> **{'**.'.join(str(user.coins).split('.'))} {Emoji.coin}\n"
                    f'{f"### favorite language:\n> {favorite_language['name'].lower()}\n" if favorite_language else ""}'
                    f"### socials:\n- [{Emoji.github}  github]({user.github})\n"
                    f'{f"- [{Emoji.wakatime}  wakatime]({wakatime_url})\n" if wakatime_url else ""}'
                    f'{f"- [portfolio]({user.portfolio})" if user.portfolio else ""}'
                ),
            ).set_author(name=user.name, icon_url=member.avatar)
        )


async def setup(bot):
    await bot.add_cog(Profile(bot))
