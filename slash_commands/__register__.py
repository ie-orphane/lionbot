import discord, requests, base64
from discord.ext import commands
from models import UserData


class register(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="register", description="register to track your coding time"
    )
    @discord.app_commands.describe(name="your full name", api_key="wakatime api key")
    async def register_command(
        self, interaction: discord.Interaction, name: str, api_key: str
    ):
        await interaction.response.defer()
        user_data = UserData.read(interaction.user.id)
        if user_data is not None:
            if user_data.token is None:
                encoded_key = base64.b64encode(api_key.encode()).decode()
                auth_header = f"Basic {encoded_key}"

                headers = {
                    "Authorization": auth_header,
                    "Content-Type": "application/json",
                }

                url = "https://wakatime.com/api/v1/users/current"
                response = requests.get(url, headers=headers)

                if response.status_code != 200:
                    print(
                        f"Error {interaction.user}: {response.status_code}, {response.text}"
                    )
                    await interaction.followup.send("Invalid API KEY!")
                    return

                user_data.token = api_key
                user_data.update()
                await interaction.followup.send("API KEY updated successfully!")
                return

            await interaction.followup.send("User already Registred!")
            return

        # create the user
        encoded_key = base64.b64encode(api_key.encode()).decode()
        auth_header = f"Basic {encoded_key}"

        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json",
        }

        url = "https://wakatime.com/api/v1/users/current"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Error {interaction.user}: {response.status_code}, {response.text}")
            await interaction.followup.send("Invalid API KEY!")
            return

        user_data.token = api_key
        user_data.update()
        UserData(name=name, coins=0, token=api_key, ledger={}).update()

        await interaction.followup.send("User Created successfully!")


async def setup(bot: commands.Bot):
    await bot.add_cog(register(bot))
