import re
import discord
from config import get_reaction
from models import QuizData
from consts import COLOR


class QuizButton(
    discord.ui.DynamicItem[discord.ui.Button],
    template=r"(?P<id>[0-9]+):(?P<key>[a-z]+)",
):
    def __init__(self, quiz_id: int | str, answer_key: str) -> None:
        super().__init__(
            discord.ui.Button(
                custom_id=f"{quiz_id}:{answer_key}",
                label=get_reaction(answer_key, ""),
            )
        )
        self.quiz_id = quiz_id
        self.answer_key = answer_key

    @classmethod
    async def from_custom_id(
        cls,
        interaction: discord.Interaction,
        button: discord.ui.Button,
        match: re.Match[str],
        /,
    ):
        return cls(match["id"], match["key"])

    async def callback(self, interaction: discord.Interaction) -> None:
        quiz: QuizData = QuizData.read(self.quiz_id)
        if str(interaction.user.id) in quiz.contributions:
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=COLOR.red,
                    description=f"{interaction.user.mention} 🚫,\nyou have already answered this quiz!\nPlease wait for the next one.",
                ),
                ephemeral=True,
            )
            return
        quiz.contributions[interaction.user.id] = self.answer_key
        quiz.update()
        await interaction.response.send_message(
            embed=discord.Embed(
                color=COLOR.green,
                description=f"{interaction.user.mention} ✅,\nyour answer has been submitted successfully!\nThanks for participating.",
            ),
            ephemeral=True,
        )


class QuizView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
