from datetime import UTC, datetime

import discord
from discord.ext import commands

from cogs import GroupCog
from config import ChallengeConfig, get_emoji
from consts import COLOR, MESSAGE
from models import EvaluationData, UserChallenge, UserData
from notations import CHALLENGE
from utils import RelativeDateTime, number


@discord.app_commands.dm_only()
class Challenge(GroupCog, name="challenge"):
    @discord.app_commands.command(description="Request a new challenge.")
    @discord.app_commands.describe(language="The Challenge's language.")
    async def request(
        self, interaction: discord.Interaction, language: CHALLENGE.LANGUAGE
    ):
        await interaction.response.defer()
        self.cog_interaction(interaction, language=language)

        if (user := await self.bot.user_is_unkown(interaction)) is None:
            return

        if (user.quests is None) or (language not in user.quests):
            await interaction.followup.send(
                embed=discord.Embed(
                    color=COLOR.red,
                    description=(
                        f"🚫 {interaction.user.mention},\n"
                        "you don't have permission to embark on this **journey**."
                    ),
                ).set_footer(text="consider contacting our staff.")
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
                        f"### {current_challenge.name}\n"
                        f"```ansi\n{current_challenge.subject}```\n"
                        f"**`Level`**: {current_challenge.level}\n"
                        f"**`Reward`**: {number(current_challenge.coins)} {get_emoji("coin")}\n"
                        f"**`Excpected File`**: {current_challenge.file}"
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
                    f"```ansi\n{challenge.subject}```\n"
                    f"**`Level`**: {challenge.level}\n"
                    f"**`Reward`**: {number(challenge.coins)} {get_emoji("coin")}\n"
                    f"**`Excpected File`**: {challenge.file}"
                ),
            ).set_footer(text="as always follow the law and doubt your code!"),
        )

    @discord.app_commands.command(description="Submit a challenge's code.")
    @discord.app_commands.describe(file="The file to submit.")
    async def submit(self, interaction: discord.Interaction, file: discord.Attachment):
        await interaction.response.defer()
        self.cog_interaction(interaction, file=file)

        if (user := await self.bot.user_is_unkown(interaction)) is None:
            return

        current_challenge = user.challenge
        if current_challenge is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, you don't have any challenge to submit!",
                ).set_footer(text="instead, use /challenge request")
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
            await file.save(solution.path)
            if current_challenge.additionales:
                with open(solution.path, "a") as f:
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
            timestamp=current_challenge.timestamp,
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
    async def status(
        self, interaction: discord.Interaction, language: CHALLENGE.LANGUAGE
    ):
        await interaction.response.defer()
        self.cog_interaction(interaction, language=language)

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
        self.cog_interaction(interaction)

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
                and challenge.id == user_log.id
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
                            f"**`Result`**: {user_log.result}\n"
                            f"**`Cost`**: {number(user_log.cost)} {get_emoji("coin")}"
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
        self.cog_interaction(interaction)

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.blue,
                description=(
                    "### /challenge request : get a new challenge\n"
                    + "- During the challenge, always follow the **law**  and doubt your code.\n"
                    + "- You have 1 day to submit your code, if you pass the deadline your challenge will be evaluated as `DEAD`.\n"
                    + "- After **7** tries of the same challenge, you will cost **7**% of the reward for every next request.\n"
                    + "### /challenge submit : send your code challenge\n"
                    + "- Your code will be evaluated by a program called **bugini**.\n"
                    + "- You will receive a message with challenge result (`OK` | `ERROR` | `KO` | `FORBIDDEN` | `TIMEOUT`).\n"
                    + "- The **reward** depend on the **difficulty** of the challenge.\n"
                    + "".join(
                        [
                            f"  - {difficulty}: {number(coins)} {get_emoji('coin')}\n"
                            for difficulty, coins in ChallengeConfig.COINS.items()
                        ]
                    )
                    + "### /challenge status : show your challenge journey\n"
                    + "- see your ancients and current challenges.\n"
                    + "### /challenge log : see the failing part of the last challenge\n"
                    + "- With a cost **5**% of the reward.\n"
                    + "- Only the `ERROR` and `KO` challenges will have a log.\n"
                ),
            )
        )


@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
class _Challenge(GroupCog, name="__challenge"):
    @discord.app_commands.command(description="Request a new challenge.")
    @discord.app_commands.describe(
        language="The challenge's language.", _geek="The geek(s) to assign."
    )
    @discord.app_commands.rename(_geek="geek")
    async def assign(
        self,
        interaction: discord.Interaction,
        language: CHALLENGE.LANGUAGE,
        _geek: discord.Member | discord.Role,
    ):
        await interaction.response.defer(ephemeral=True)
        self.cog_interaction(interaction, language=language, geek=_geek)

        geeks: list[discord.Member] = []
        users: list[UserData] = []
        not_registred: list[discord.Member] = []

        if isinstance(_geek, discord.Member):
            geeks.append(_geek)
        elif isinstance(_geek, discord.Role):
            geeks = _geek.members

        for geek in geeks:
            if (user := UserData.read(geek.id)) is None:
                not_registred.append(geek)
                continue
            users.append(user)

        if not_registred:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=COLOR.red,
                    description=(
                        f"✋ {interaction.user.mention},\n\n"
                        + f"{'Geeks are' if len(not_registred) > 1 else 'A geek is'} not registered yet!\n"
                        + "\n".join([f" - {geek.mention}" for geek in not_registred])
                    ),
                ),
                ephemeral=True,
            )
            return

        for user in users:
            user.add_quest(language)

        await interaction.followup.send(
            embed=discord.Embed(
                color=COLOR.yellow,
                description=(
                    f"⚔️ {interaction.user.mention},\n\n"
                    + f"you assigned the **{language}** {get_emoji(language)} quest to:\n"
                    + "\n".join([f"- {geek.mention}" for geek in geeks])
                ),
            ),
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Challenge(bot))
    await bot.add_cog(_Challenge(bot))
