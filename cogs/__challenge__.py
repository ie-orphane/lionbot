import discord
from discord.ext import commands
from models import UserData, EvaluationData, ChallengeData
from bot.config import Emoji
from datetime import datetime, UTC
from utils import Language, MESSAGE, COLOR, RelativeDateTime


@discord.app_commands.default_permissions(send_messages=False)
class Challenge(commands.GroupCog, name="challenge"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.color = COLOR

    @discord.app_commands.command(description="request new challenge")
    @discord.app_commands.describe(language="challenge language")
    async def request(self, interaction: discord.Interaction, language: Language):
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

        current_challenge = user.challenge
        if current_challenge:
            if current_challenge.submited:
                await interaction.followup.send(
                    embed=discord.Embed(
                        color=self.color.red,
                        description=f"**{current_challenge.name}** {MESSAGE.waiting}",
                    ).set_footer(text="be patient!")
                )
                return

            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=(
                        f"### {interaction.user.mention}, you already requested a challenge!\n"
                        f"```txt\n{current_challenge.text}```\n"
                        f"**Level**: {current_challenge.level}\n"
                        f"**Rewards**: {current_challenge.points} {Emoji.star} & {current_challenge.coins} {Emoji.coin}"
                    ),
                )
            )
            return

        challenge = user.request_challenge(language)
        if challenge is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.yellow,
                    description=f"### {interaction.user.mention}\n**{MESSAGE.finishing}**",
                )
            )
            return

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.yellow,
                description=(
                    f"```txt\n{challenge.text}```\n"
                    f"**Level**: {challenge.level}\n"
                    f"**Rewards**: {challenge.points} {Emoji.star} & {challenge.coins} {Emoji.coin}"
                ),
            ).set_footer(text="as always follow the law and doubt your code!"),
            ephemeral=True,
        )

    @discord.app_commands.command(description="submit a challenge code")
    @discord.app_commands.describe(file="file to submit")
    async def submit(self, interaction: discord.Interaction, file: discord.Attachment):
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

        current_challenge = user.challenge
        if current_challenge is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, you don't have any challenge to submit!",
                ).set_footer(text="use /challenge request instead")
            )
            return

        if current_challenge.submited:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"**{current_challenge.name}** {MESSAGE.waiting}",
                ).set_footer(text="be patient!")
            )
            return

        if file.filename != current_challenge.file:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"Excepected file **{current_challenge.file}** got **{file.filename}** .",
                ).set_footer(text="strange file!")
            )
            return

        try:
            solution = f"{int(datetime.now(UTC).timestamp())}.{current_challenge.exe}"
            await file.save(f"assets/solutions/{solution}")
        except Exception as e:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"Failed to read {file.filename} .",
                ).set_footer(text="Suspicious File!")
            )
            print(f"failed to read {file.filename} from {user.name}\nError: {e}")
            return

        user._challenge.update({"submited": str(datetime.now(UTC))})
        EvaluationData.create(
            user=user.id,
            solution=solution,
            language=current_challenge.language,
            level=current_challenge.level,
        )
        user.update()

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                description=f"**{current_challenge.name}** {MESSAGE.submiting}",
            ).set_footer(text="Diving into your code!")
        )

    @discord.app_commands.command(description="see the history of your journey")
    @discord.app_commands.describe(language="challenge language")
    async def status(self, interaction: discord.Interaction, language: Language):
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

        all_challenges: dict[tuple[int, str], list[ChallengeData]] = {}

        for challenge in user.challenges:
            all_challenges.setdefault((challenge.level, challenge.name), [])
            all_challenges[(challenge.level, challenge.name)].append(challenge)

        all_challenges = dict(sorted(all_challenges.items(), key=lambda x: x[0][0]))

        solved = 0
        content = ""
        for challenge_info, challenges in all_challenges.items():
            challenges.sort(key=lambda x: x.time)
            content += f"\n{challenge_info[0]} : {challenge_info[1]}\n"
            for challenge in challenges:
                if challenge.result == "OK":
                    solved += 1
                content += f"\t {challenge.time}  {challenge.result:^7}  {RelativeDateTime(datetime.fromisoformat(challenge.requested)).pretty}\t\n"
        content = f"Total  : {len(all_challenges)}\nSolved : {solved}\n{content}"

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.yellow,
                description=f"```txt\n{content}```",
            )
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Challenge(bot))
