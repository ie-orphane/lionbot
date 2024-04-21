import discord
from discord.ext import commands
from models import UserData
from utils import dclr
from typing import Union


class profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="profile", description="view your profile")
    @discord.app_commands.describe(member="see member profile")
    async def profile_command(
        self,
        interaction: discord.Interaction,
        member: Union[discord.Member, discord.User] = None,
    ):
        await interaction.response.defer()

        member = member or interaction.user
        user_data = UserData.read(member.id)

        if user_data is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=dclr.red,
                    description=f"{member.mention}{', you are' if member == interaction.user else ' is'} not registered yet!",
                )
            )
            return

        await interaction.followup.send(
            embed=discord.Embed(
                color=dclr.yellow,
                description=(
                    f'{"### class:\n> **Coding** - Web Development **II**\n" if user_data.training == "codingII" else ""}'
                    f"### coins:\n> **{'**.'.join(str(user_data.coins).split('.'))} <:lioncoin:1219417317419651173>\n"
                    f"### socials:\n- [<:github:1231551666075996190> github]({user_data.github})\n"
                    f'{f"- [portfolio]({user_data.portfolio})" if user_data.portfolio else ""}'
                ),
            ).set_author(name=user_data.name, icon_url=member.avatar)
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(profile(bot))
