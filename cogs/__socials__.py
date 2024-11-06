import discord
from discord.ext import commands
from models import UserData
from utils import Social, COLOR


@discord.app_commands.default_permissions(send_messages=False)
class Socials(commands.GroupCog, name="socials"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.color = COLOR

    @discord.app_commands.command(description="add a new social link")
    @discord.app_commands.describe(link="social link")
    async def add(self, interaction: discord.Interaction, social: Social, link: str):
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

        if user.socials.exists(social):
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"**{social}** social already added to your profile !",
                )
            )
            return

        user._socials[social] = link
        user.update()

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                description=f"{social} social added succefuly",
            ).set_footer(text="check your profile using /profile"),
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Socials(bot))
