import discord
import requests
from models import UserData
from string import ascii_letters
from cogs import Cog


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
                )
            )
            return

        if [char for char in name if char not in ascii_letters + " "]:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"Invalid name **{name}**.",
                )
            )
            return

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

        UserData(
            id=interaction.user.id,
            name=" ".join([word.capitalize() for word in name.split()]),
            coins=0,
            token=waka_token,
            github=None,
            training=None,
            portfolio=None,
            points=0,
            _challenges=[],
            graduated=False,
        ).update()

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                description=f"{interaction.user.mention}, your registred successfully!",
            )
        )


async def setup(bot):
    await bot.add_cog(Register(bot))
