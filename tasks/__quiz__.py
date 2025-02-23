import discord
from datetime import datetime, UTC
from utils import Log, charts, number
from api import QuizApi
from models import QuizData, UserData
from config import get_emoji, get_reaction
from consts import Quiz
from discord.ext import tasks, commands


@tasks.loop(seconds=45)
async def quiz(bot: commands.Bot):
    channel: discord.TextChannel
    message: discord.Message
    now = datetime.now(UTC)

    if (channel := bot.get_listed_channel("events")) is None:
        return

    current_quiz = QuizData.last()

    if (current_quiz and not current_quiz.ended) and (
        Quiz.END_TIME <= (now.hour, now.minute)
        or (now.hour, now.minute) < Quiz.START_TIME
    ):
        if (message := await channel.fetch_message(current_quiz.message_id)) is None:
            return

        Log.job("Quiz", "Ending trivia event...")
        _reactions: dict[int, discord.Reaction] = {}
        users_to_purne: list[discord.User] = []
        for reaction in message.reactions:
            if not reaction.me:
                await reaction.clear()
                continue
            async for user in reaction.users():
                if user == bot.user:
                    continue
                if user in users_to_purne:
                    await reaction.remove(user)
                    continue
                if user.id in _reactions:
                    await reaction.remove(user)
                    await _reactions.pop(user.id).remove(user)
                    users_to_purne.append(user)
                    continue
                _reactions[user.id] = reaction
        reactions: dict[str, int] = dict.fromkeys(current_quiz.answers, 0)
        current_quiz.contributors = []
        for user_id, reaction in _reactions.items():
            answerkey = current_quiz.emojis[str(reaction)]
            reactions.setdefault(answerkey, 0)
            reactions[answerkey] += 1
            if current_quiz.correct_answers[answerkey]:
                current_quiz.contributors.append(user_id)
            if (winner := UserData.read(user_id)) is not None:
                winner.add_coins(
                    Quiz.REWARD_AMOUNT.get(current_quiz.difficulty, 0), "quiz win"
                )
        current_quiz.ended = True
        current_quiz.update()
        embed = discord.Embed(
            color=current_quiz.color,
            description=(
                f"{":partying_face:" if len(current_quiz.contributors) != 0 else ':pensive:'} **Winner(s)**: **{len(current_quiz.contributors)}**\n"
                f"{''.join([f"- <@{user_id}>\n" for user_id in current_quiz.contributors])}\n"
                f":white_check_mark: **Correct answer(s)**:\n"
                f"{'\n'.join([f"- {get_emoji(answerkey)} {answer}" for answerkey, answer in current_quiz.answers.items() if current_quiz.correct_answers[answerkey]])}"
            ),
        )
        if show_statistics := len(current_quiz.contributors) != 0:
            charts.answers(reactions, current_quiz.correct_answers.values(), "summary")
            file = discord.File(f"./assets/images/summary.png", filename=f"summary.png")
            embed.set_image(url="attachment://summary.png")
            embed.description += f"\n\n:bar_chart: **Statistics**:"
        await message.reply(file=file if show_statistics else None, embed=embed)
        Log.job("Quiz", "Trivia ended.")
        return

    if ((current_quiz is None) or (now.date() > current_quiz.date)) and (
        Quiz.START_TIME <= (now.hour, now.minute) < Quiz.END_TIME
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
        message: discord.Message = await channel.send(embed=embed)
        for answerkey in current_quiz.answers:
            if (emoji := get_reaction(answerkey, None)) is not None:
                await message.add_reaction(emoji)
                current_quiz.emojis[emoji] = answerkey
        current_quiz.message_id = message.id
        current_quiz.date = now.date()
        current_quiz.update()
        Log.job("Quiz", "Trivia started.")
        return
