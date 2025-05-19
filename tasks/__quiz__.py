from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands, tasks

import env
from api import QuizApi
from config import get_emoji, get_reaction
from consts import Quiz
from models import QuizData, UserData
from ui import QuizButton, QuizView
from utils import Log, charts, number


@tasks.loop(seconds=45)
async def quiz(bot: commands.Bot):
    try:
        channel: discord.TextChannel
        message: discord.Message
        now = datetime.now(ZoneInfo("Africa/Casablanca"))

        if (channel := bot.get_listed_channel("events")) is None:
            return

        current_quiz = QuizData.last()

        if (current_quiz and not current_quiz.ended) and (
            Quiz.END_TIME <= (now.hour, now.minute)
            or (now.hour, now.minute) < Quiz.START_TIME
        ):
            if (
                message := await channel.fetch_message(current_quiz.message_id)
            ) is None:
                return
            Log.job("Quiz", "Ending trivia event...")
            await message.edit(view=None)
            answers: dict[str, int] = {answer: 0 for answer in current_quiz.answers}
            winners: list[str] = []
            for user_id, answerkey in current_quiz.contributions.items():
                answers[answerkey] += 1
                if not current_quiz.correct_answers[answerkey]:
                    continue
                winners.append(user_id)
                if (winner := UserData.read(user_id)) is not None:
                    winner.add_coins(
                        Quiz.REWARD_AMOUNT.get(current_quiz.difficulty, 0), "quiz win"
                    )
            current_quiz.ended = True
            current_quiz.update()
            shoW_details: bool = len(winners) != 0
            embed = discord.Embed(
                color=current_quiz.color,
                description=(
                    f"{":partying_face:" if shoW_details else ':pensive:'} **Winner(s)**: **{len(winners)}**\n"
                    f"{''.join([f"- <@{user_id}>\n" for user_id in winners])}\n"
                    f":white_check_mark: **Correct answer(s)**:\n"
                    f"{'\n'.join([f"- {get_reaction(answerkey)} {answer}" for answerkey, answer in current_quiz.answers.items() if current_quiz.correct_answers[answerkey]])}"
                ),
            )
            if current_quiz.explanation:
                embed.description += (
                    f"\n\n:book: **Explanation**:\n{current_quiz.explanation}"
                )
            if shoW_details:
                await charts.answers(
                    answers, current_quiz.correct_answers.values(), "summary"
                )
                file = discord.File(
                    f"{env.BASE_DIR}/storage/images/summary.png",
                    filename=f"summary.png",
                )
                embed.set_image(url="attachment://summary.png")
                embed.description += f"\n\n:bar_chart: **Statistics**:"
            await message.reply(file=file if shoW_details else None, embed=embed)
            Log.job("Quiz", "Trivia ended.")
            return

        if (
            ((current_quiz is None) or (now.date() > current_quiz.date))
            and (Quiz.START_TIME <= (now.hour, now.minute) < Quiz.END_TIME)
            and now.weekday() in Quiz.DAYS
        ):
            Log.job("Quiz", "Starting trivia event...")
            current_quiz = await QuizApi.get()
            embed = discord.Embed(
                description=f"**{current_quiz.question}**\n", color=current_quiz.color
            )
            if current_quiz.description:
                embed.description += current_quiz.description + "\n"
            embed.description += (
                f"\n**Answers:** \n{"\n".join([f":regional_indicator_{answerkey}:  {answer}"for answerkey, answer in current_quiz.answers.items()])}\n\n"
                f"**Reward**: {number(Quiz.REWARD_AMOUNT[current_quiz.difficulty])} {get_emoji("coin")}\n"
                f"**Ends**: <t:{int(now.replace(hour=Quiz.END_TIME[0], minute=Quiz.END_TIME[1]).timestamp())}:R>\n"
                f"**Difficulty**: {current_quiz.difficulty}\n"
                f"**Multi-answers**: {current_quiz.multiple_correct_answers}\n"
                f"**Category**: {current_quiz.category} {''.join([f"#{tag} {get_emoji(tag, '')} " for tag in current_quiz.tags])}"
            )
            view = QuizView()
            for answerkey in current_quiz.answers:
                view.add_item(QuizButton(current_quiz.id, answerkey))
            message: discord.Message = await channel.send(embed=embed, view=view)
            current_quiz.message_id = message.id
            current_quiz.date = now.date()
            current_quiz.update()
            Log.job("Quiz", "Trivia started.")
            return
    except Exception as e:
        Log.error("Quiz", e)
