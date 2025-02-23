import discord
from discord.ext import commands
from models import EvaluationData, UserChallenge
from config import get_emoji
from datetime import datetime, UTC
from utils import Language, RelativeDateTime
from consts import MESSAGE
from cogs import GroupCog


@discord.app_commands.dm_only()
class Challenge(GroupCog, name="challenge"):
    @discord.app_commands.command(description="Request a new challenge.")
    @discord.app_commands.describe(language="The Challenge's language.")
    async def request(self, interaction: discord.Interaction, language: Language):
        await interaction.response.defer()

        if (user := await self.bot.user_is_unkown(interaction)) is None:
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
                        f"### {current_challenge.name}\n"
                        f"```ansi\n{current_challenge.text}```\n"
                        f"**Level** : {current_challenge.level}\n"
                        f"**Reward** : {current_challenge.coins} {get_emoji("coin")}\n"
                        f"**Excpected File** : {current_challenge.file}"
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
                title=challenge.name,
                description=(
                    f"```ansi\n{challenge.text}```\n"
                    f"**Level** : {challenge.level}\n"
                    f"**Reward** : {challenge.coins} {get_emoji("coin")}\n"
                    f"**Excpected File** : {challenge.file}"
                ),
            ).set_footer(text="as always follow the law and doubt your code!"),
        )

    @discord.app_commands.command(description="Submit a challenge's code.")
    @discord.app_commands.describe(file="The file to submit.")
    async def submit(self, interaction: discord.Interaction, file: discord.Attachment):
        await interaction.response.defer()

        if (user := await self.bot.user_is_unkown(interaction)) is None:
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
            solution = current_challenge.solution
            await file.save(solution)
            if current_challenge.additionales:
                with open(solution, "a") as f:
                    print(current_challenge.additionales, file=f)
        except discord.errors.HTTPException or discord.errors.NotFound as e:
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
            user=user,
            solution=solution,
            challenge=current_challenge,
        )
        user._log = None
        user.update()

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                description=f"**{current_challenge.name}** {MESSAGE.submiting}",
            ).set_footer(text="Diving into your code!")
        )

    @discord.app_commands.command(description="See the history of your journey.")
    @discord.app_commands.describe(language="The language of the challenges.")
    async def status(self, interaction: discord.Interaction, language: Language):
        await interaction.response.defer()

        if (user := await self.bot.user_is_unkown(interaction)) is None:
            return

        all_challenges: dict[tuple[int, str], list[UserChallenge]] = {}

        for challenge in user.challenges:
            if challenge.language == language:
                all_challenges.setdefault((challenge.level, challenge.name), [])
                all_challenges[(challenge.level, challenge.name)].append(challenge)
        if current_challenge := user.challenge:
            if current_challenge.language == language:
                all_challenges.setdefault(
                    (current_challenge.level, current_challenge.name), []
                )
                current_challenge.result = "CURRENT"
                all_challenges[
                    (current_challenge.level, current_challenge.name)
                ].append(current_challenge)

        all_challenges = dict(sorted(all_challenges.items(), key=lambda x: x[0][0]))

        solved = 0
        content = ""
        for challenge_info, challenges in all_challenges.items():
            challenges.sort(key=lambda x: x.attempt)
            content += f"\n{challenge_info[0]} : {challenge_info[1]}\n"
            for challenge in challenges:
                if challenge.result == "OK":
                    solved += 1
                content += f"\t [{challenge.attempt}]  {challenge.result:^9}  {RelativeDateTime(challenge.requested).pretty}\t\n"
        content = f"Total  : {len(all_challenges)}\nSolved : {solved}\n{content}"

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.yellow, description=f"```txt\n{content}```"
            )
        )

    @discord.app_commands.command(description="See a failed challenge log.")
    async def log(self, interaction: discord.Interaction):
        await interaction.response.defer()

        if (user := await self.bot.user_is_unkown(interaction)) is None:
            return

        user_log = user.log
        if user_log is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, no logs were found.",
                )
            )
            return

        for challenge in user.challenges:
            if (
                challenge.language == user_log.language
                and challenge.level == user_log.level
                and challenge.attempt == user_log.attempt
            ):
                user.sub_coins(user_log.cost, "log cost")
                user._log = None
                user.update()
                await interaction.followup.send(
                    embed=discord.Embed(
                        color=self.color.orange,
                        title=user_log.name,
                        description=(
                            f"```ansi\n{user_log.trace}```\n"
                            f"**Result** : {user_log.result}\n"
                            f"**Cost** : {user_log.cost} {get_emoji("coin")}"
                        ),
                    )
                )
                return

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.red,
                description=f"{interaction.user.mention}, no logs were found.",
            )
        )

    @discord.app_commands.command(description="Show the challenge's guidlines.")
    async def help(self, interaction: discord.Interaction):
        await interaction.response.defer()

        with open("assets/challenges.md", "r") as f:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.blue,
                    description="\n".join(
                        [
                            "### /challenge request : get a new challenge"
                            "- During the challenge, always follow the **law**  and doubt your code."
                            "- You have 1 day to submit your code, if you pass the deadline your challenge will be evaluated as `DEAD`."
                            "- After **7** tries of the same challenge, you will cost **7**% of the reward for every next request."
                            "### /challenge submit : send your code challenge"
                            "- Your code will be evaluated by a program called **bugini**."
                            "- You will receive a message with challenge result (`OK` | `ERROR` | `KO` | `FORBIDDEN` | `TIMEOUT`)."
                            "- The **reward** depend on the **difficulty** of the challenge."
                            "### /challenge status : show your challenge journey"
                            "- see your ancients and current challenges."
                            "### /challenge log : see the failing part of the last challenge"
                            "- With a cost **5**% of the reward."
                            "- Only the `ERROR` and `KO` challenges will have a log."
                        ]
                    ),
                )
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Challenge(bot))
