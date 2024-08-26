import discord
import subprocess
from discord.ext import commands
from models import UserData
from bot.config import CHANNELS, Emoji, COMMAND
from cogs import COLOR
from datetime import datetime, UTC


class Challenge(commands.GroupCog, name="challenge"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.color = COLOR()

    @discord.app_commands.guild_only()
    @discord.app_commands.command(description="request new challenge")
    async def request(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user = UserData.read(interaction.user.id)

        if user is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, you are' not registered yet!",
                ).set_footer(text="use /register instead")
            )
            return

        current_challenge = user.current_challenge
        if current_challenge is not None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=(
                        f"### {interaction.user.mention}, you already requested a challenge!\n"
                        f"**Instructions**\n```txt\n{current_challenge.instructions}```\n"
                        f"{f"**Input**\n```js\n{current_challenge.input}```\n" if current_challenge.input else ""}"
                        f"**Output**\n```bash\n{current_challenge.output}```\n"
                        f"**Rewards**: {current_challenge.points} {Emoji.star} & {current_challenge.coins} {Emoji.coin}\n"
                        f"**Difficulty**: {current_challenge.difficulty}"
                    ),
                )
            )
            return

        challenge = user.request_challenge()

        if challenge is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.yellow,
                    description=f"### {interaction.user.mention}\n**{user.master_message}**",
                )
            )
            return

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.yellow,
                description=(
                    f"**Instructions**\n```txt\n{challenge.instructions}```\n"
                    f"{f"**Input**\n```js\n{challenge.input}```\n" if challenge.input else ""}"
                    f"**Output**\n```bash\n{challenge.output}```\n"
                    f"**Rewards**: {challenge.points} {Emoji.star} & {challenge.coins} {Emoji.coin}\n"
                    f"**Difficulty**: {challenge.difficulty}"
                ),
            ).set_footer(text="happy coding !"),
            ephemeral=True,
        )

    @discord.app_commands.guild_only()
    @discord.app_commands.command(description="submit a challenge code")
    async def submit(self, interaction: discord.Interaction, code: str):
        await interaction.response.defer()
        user = UserData.read(interaction.user.id)

        if user is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, you are' not registered yet!",
                ).set_footer(text="use /register instead")
            )
            return

        current_challenge = user.current_challenge
        if current_challenge is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, you don't have any challenge to submit!",
                ).set_footer(text="use /challenge request instead")
            )
            return

        if current_challenge.submited is not None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, you already submited the challenge!",
                ).set_footer(text="be patient!")
            )
            return

        result = subprocess.run([COMMAND, "-e", code], text=True, capture_output=True)

        if result.stderr:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    title="Failed to submit the code !",
                    description=f"```bash\n{"\n".join(result.stderr.splitlines()[:-3])}\n```",
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
                description=(
                    f"**Challange**\n```\nInstructions:\n{current_challenge.instructions}\n"
                    f"{'Input:\n' + current_challenge.input if current_challenge.input else ""}\n"
                    f"Output:\n{current_challenge.output}```\n"
                    f"**Code**:\n```js\n{code}\n```\n**Result**:\n```bash\n{result.stdout}\n```"
                    f"\n**Approve Code**: ```txt\n{user.id}-{current_challenge.id}\n```"
                ),
            )
            .set_author(name=user.name, icon_url=interaction.user.avatar)
            .set_footer(text=f"Difficulty:  {current_challenge.difficulty}")
        )

        user._challenges[str(current_challenge.id)].update(
            {"submited": str(datetime.now(UTC))}
        )
        user.update()

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                title="Code submited successfully !",
                description=f"**Result**:\n```bash\n{result.stdout}\n```",
            )
        )

    # @discord.app_commands.default_permissions(administrator=True)
    # @discord.app_commands.command(description="approve a challenge code")
    # async def approve(self, interaction: discord.Interaction, challenge_code: str):
    #     await interaction.response.defer()

    #     if challenge_code.count('-') != 1:
    #         await interaction.followup.send(
    #             embed=discord.Embed(
    #                 color=self.color.red,
    #                 description=f"`{challenge_code}` is an invalid code challenge",
    #             )
    #         )
    #         return

    #     user_id, challenge_id = challenge_code.split("-")

    #     user = UserData.read(user_id)
    #     if user is None:
    #         await interaction.followup.send(
    #             embed=discord.Embed(
    #                 color=self.color.red,
    #                 description=f"User with ID `{user_id}` not found !",
    #             )
    #         )
    #         return

    #     challenge = user.get_challenge(challenge_id)

    #     if challenge is None:
    #         await interaction.followup.send(
    #             embed=discord.Embed(
    #                 color=self.color.red,
    #                 description=f"{user.name} has no challenge `{challenge_id}` !",
    #             )
    #         )
    #         return

    #     if challenge.approved:
    #         await interaction.followup.send(
    #             embed=discord.Embed(
    #                 color=self.color.red,
    #                 description=f"Challenge `{challenge_id}` already approved!",
    #             )
    #         )
    #         return

    #     user._challenges[challenge_id].update({"approved": str(datetime.now(UTC))})
    #     user.coins += challenge.coins
    #     user.points += challenge.points
    #     user.update()

    #     try:
    #         discord_user = await self.bot.fetch_user(user_id)
    #         await discord_user.send(
    #             embed=discord.Embed(
    #                 color=self.color.yellow,
    #                 description=f"{user.approve_message}\n\nYou gain **{challenge.coins}** {Emoji.coin} & **{challenge.points}** {Emoji.star}",
    #         ))
    #     except Exception as e:
    #         print(f"Error: {[e]}")

    #     await interaction.followup.send(
    #         embed=discord.Embed(
    #             color=self.color.green,
    #             description=f"**{user.name}**'s current challenge has been approved !",
    #         )
    #     )

async def setup(bot: commands.Bot):
    await bot.add_cog(Challenge(bot))
