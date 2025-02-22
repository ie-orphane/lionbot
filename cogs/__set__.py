import discord
from discord.ext import commands
from models import UserData
from utils import Social
from config import get_emoji
from cogs import GroupCog
from api import wakapi


@discord.app_commands.guild_only()
class Set(GroupCog, name="set"):
    @discord.app_commands.command(description="Set a new social link.")
    @discord.app_commands.describe(social="The social's name.", link="The social's link.")
    async def social(self, interaction: discord.Interaction, social: Social, link: str):
        await interaction.response.defer()
        user = UserData.read(interaction.user.id)

        if user is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, you are not registered yet!",
                ).set_footer(text="use /register instead"),
                ephemeral=True,
            )
            return

        new_link = user.add_social(social, link)
        if not new_link:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"Oops! The {social} link '**{link}**' maybe invalid !",
                ),
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                description=f"[{get_emoji(social)}{social}]({new_link}) social added succefuly",
            ).set_footer(text="check your profile using /profile"),
            ephemeral=True,
        )

    @discord.app_commands.command(description="Reset your wakatime api token.")
    @discord.app_commands.describe(waka_token="The new wakatime token.")
    async def token(self, interaction: discord.Interaction, waka_token: str):
        await interaction.response.defer()
        user = UserData.read(interaction.user.id)

        if user is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, you are not registered yet!",
                ).set_footer(text="use /register instead"),
                ephemeral=True,
            )
            return
        
        if (await wakapi.get_current(waka_token)) is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"Invalid Wakatime API KEY `{waka_token}`.",
                ),
                ephemeral=True,
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
