import discord
from models import UserData
from string import ascii_letters
from cogs import Cog
from api import wakapi


class Register(Cog):
    @discord.app_commands.command(description="register to track your coding time")
    @discord.app_commands.guild_only()
    @discord.app_commands.describe(
        name="your full name",
        waka_token="Wakatime api key",
    )
    async def register(
        self,
        interaction: discord.Interaction,
        name: discord.app_commands.Range[str, 5, 25],
        waka_token: str,
    ):
        await interaction.response.defer()

        user_data = UserData.read(interaction.user.id)

        if user_data is not None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, you are already registered!",
                ),
                ephemeral=True,
            )
            return

        if [char for char in name if char not in ascii_letters + " "]:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"Invalid name **{name}**.",
                ),
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

        UserData(
            id=interaction.user.id,
            name=" ".join([word.capitalize() for word in name.split()]),
            coins=0,
            token=waka_token,
            training=None,
            graduated=False,
            _challenges=[],
            _challenge=None,
            _socials={},
        ).update()

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                description=f"{interaction.user.mention}, your registred successfully!",
            ),
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(Register(bot))
