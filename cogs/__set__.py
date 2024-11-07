import discord
from discord.ext import commands
from models import UserData
from utils import Social, COLOR
from bot.config import Emoji


@discord.app_commands.default_permissions(send_messages=False)
class Set(commands.GroupCog, name="set"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.color = COLOR

    @discord.app_commands.command(description="set a new social link")
    @discord.app_commands.describe(link="social link")
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
                description=f"[{Emoji.get(social)}{social}]({new_link}) social added succefuly",
            ).set_footer(text="check your profile using /profile"),
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Set(bot))
