import discord
import requests
from discord.ext import commands
from models import UserData
from utils import Social
from config import get_emoji
from constants import COLOR


@discord.app_commands.guild_only()
class Set(commands.GroupCog, name="set"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.color = COLOR

    @discord.app_commands.command(description="set a new social link")
    @discord.app_commands.describe(social="social name", link="social link")
    async def social(self, interaction: discord.Interaction, social: Social, link: str):
        await interaction.response.defer()
        user = UserData.read(interaction.user.id)

        if user is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, you are not registered yet!",
                ).set_footer(text="use /register instead")
            )
            return

        new_link = user.add_social(social, link)
        if not new_link:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"Oops! The {social} link '**{link}**' maybe invalid !",
                )
            )
            return

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                description=f"[{get_emoji(social)}{social}]({new_link}) social added succefuly",
            ).set_footer(text="check your profile using /profile"),
        )

    @discord.app_commands.command(description="set a new wakatime token")
    @discord.app_commands.describe(waka_token="the new wakatime token")
    async def token(self, interaction: discord.Interaction, waka_token: str):
        await interaction.response.defer()
        user = UserData.read(interaction.user.id)

        response = requests.get(
            url="https://wakatime.com/api/v1/users/current",
            headers={
                "Authorization": f"Basic {waka_token}",
                "Content-Type": "application/json",
            },
        )

        if not response.ok:
            print(f"Error {interaction.user}: {response.status_code}, {response.text}")
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"Invalid Wakatime API KEY `{waka_token}`.",
                )
            )
            return

        user.token = waka_token
        user.update()

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                description=f"{interaction.user.mention}, token reseted successfully!",
            )
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Set(bot))
