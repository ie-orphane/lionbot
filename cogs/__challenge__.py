import discord
import subprocess
from discord.ext import commands
from models import UserData
from bot.config import CHANNELS, Emoji
from cogs import COLOR

@discord.app_commands.guild_only()
class Challenge(commands.GroupCog, name="challenge"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.color = COLOR()

    @discord.app_commands.command(description="request new challenge")
    async def request(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user = UserData.read(interaction.user.id)

        if user is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, you are' not registered yet!",
                )
            )
            return

        challenge = user.random_challenge

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.yellow,
                description=(
                    f"**Instructions**\n```txt\n{challenge.instructions}```\n"
                    f"{f"**Input**\n```js\n{challenge.input}```\n" if challenge.input else ""}"
                    f"**Output**\n```bash\n{challenge.output}```\n"
                    f"**Rewards**: {challenge.reward} {Emoji.coin}"
                ),
            ).set_footer(text="happy coding !"),
            ephemeral=True,
        )

    @discord.app_commands.command(description="submit a challenge code")
    async def submit(self, interaction: discord.Interaction, code: str):
        await interaction.response.defer()
        user = UserData.read(interaction.user.id)

        if user is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, you are' not registered yet!",
                )
            )
            return
        
        result = subprocess.run(["bun", "-e", code], text=True, capture_output=True)

        if result.stderr:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    title="Failed to submit the code !",
                    description=f"```bash\n{"\n".join(result.stderr.splitlines()[:-1])}\n```",
                )
            )
            return
        
        if not result.stdout:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    title="Failed to submit the code !",
                    description=f"```bash\nyour Javascript code ran without an output\n```",
                )
            )
            return
        
        await self.bot.get_channel(CHANNELS.challenges).send(
            embed=discord.Embed(
                color=self.color.orange,
                description=f"**Code**:\n```js\n{code}\n```\n**Result**:\n```bash\n{result.stdout}\n```",
            )
            .set_footer(text=f"challenge code: {user.id}-{0}")
            .set_author(name=user.name, icon_url=interaction.user.avatar)
        )

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                title="Code submited successfully !",
                description=f"**Code**:\n```js\n{code}\n```\n**Result**:\n```bash\n{result.stdout}\n```",
            )
        )

    @discord.app_commands.command(description="validate a challenge code")
    async def validate(self, interaction: discord.Interaction, code: str):
        await interaction.response.defer()

        await self.bot.get_channel(CHANNELS.challenges).send(f"```js\n{code}```")


async def setup(bot: commands.Bot):
    await bot.add_cog(Challenge(bot))
