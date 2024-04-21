import discord, requests
from discord.ext import commands
from models import UserData
from utils import dclr
from string import ascii_letters

class Register(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="register", description="register to track your coding time"
    )
    @discord.app_commands.guild_only()
    @discord.app_commands.describe(
        name="your full name",
        github="your github user name",
        api_key="Wakatime api key",
    )
    async def register_command(
        self,
        interaction: discord.Interaction,
        name: discord.app_commands.Range[str, 5, 25],
        github: str,
        api_key: str,
    ):
        await interaction.response.defer()

        user_data = UserData.read(interaction.user.id)

        if user_data is not None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=dclr.red,
                    description=f"{interaction.user.mention}, you are already registered!",
                )
            )
            return
        
        if [char for char in name if char not in ascii_letters + " "]:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=dclr.red,
                    description=f"Invalid name **{name}**!",
                )
            )
            return

        response = requests.get(
            url="https://wakatime.com/api/v1/users/current",
            headers={
                "Authorization": f"Basic {api_key}",
                "Content-Type": "application/json",
            },
        )

        if response.status_code != 200:
            print(f"Error {interaction.user}: {response.status_code}, {response.text}")
            await interaction.followup.send(
                embed=discord.Embed(
                    color=dclr.red,
                    description=f"Invalid Wakatime API KEY `{api_key}`!",
                )
            )
            return

        response = requests.get(url=f"https://api.github.com/users/{github}")
        if response.status_code != 200:
            print(f"Error {interaction.user}: {response.status_code}, {response.text}")
            await interaction.followup.send(
                embed=discord.Embed(
                    color=dclr.red,
                    description=f"Invalid github username **{github}**!",
                )
            )
            return

        UserData(
            id=interaction.user.id,
            name=" ".join([word.capitalize() for word in name.split()]),
            coins=0,
            token=api_key,
            github=response.json()["html_url"],
            training=None,
            portfolio=None,
        ).update()

        await interaction.followup.send(
            embed=discord.Embed(
                color=dclr.green,
                description=f"{interaction.user.mention}, your registred successfully!",
            )
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Register(bot))
