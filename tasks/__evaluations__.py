import subprocess
import discord
from discord.ext import tasks
from discord.ext.commands import Bot
from models import EvaluationData
from datetime import datetime, UTC
from utils import clr, log, COLOR, MESSAGE
from bot.config import Emoji


@tasks.loop(minutes=1.75)
async def evaluations(bot: Bot):
    for evaluation in EvaluationData.read_all():
        print(
            log(
                "Task",
                clr.yellow,
                "Evaluation",
                f"{evaluation.challenge.name} from {evaluation.user.name}",
            )
        )

        result = "OK"
        for test in evaluation.challenge.tests:
            feedback = " ".join(["$>", evaluation.challenge.file] + test.args)
            try:
                completed_process = subprocess.run(
                    ["sh", f"assets/solutions/{evaluation.solution}"] + test.args,
                    capture_output=True,
                    text=True,
                    timeout=4,
                )
            except subprocess.TimeoutExpired:
                result = "TIMEOUT"
                break

            if completed_process.stderr:
                feedback += f"\n{completed_process.stderr}"
                result = "ERROR"
                break

            if completed_process.stdout != test.expected:
                feedback += f"\n{completed_process.stdout}"
                result = "KO"
                break

        if result == "OK":
            feedback += f"\n{completed_process.stdout}"
            evaluation.user.add_coins(evaluation.challenge.coins, "challange reward")

        evaluation.user._challenge.update(
            {
                "evaluated": str(datetime.now(UTC)),
                "solution": evaluation.solution,
                "result": result,
                "log": feedback,
            }
        )

        evaluation.user._challenges.append(evaluation.user._challenge)
        evaluation.user._challenge = None

        evaluation.user.update()

        try:
            discord_user = await bot.fetch_user(evaluation.user.id)
            await discord_user.send(
                embed=(
                    discord.Embed(
                        color=COLOR.green,
                        description=(
                            f"{MESSAGE.succeeding}\n\nChallenge : **{evaluation.challenge.name}"
                            f"**\nLanguage : {evaluation.challenge.language}\nLevel : "
                            f"{evaluation.challenge.level}\nResult : **{result}**\n"
                            f"Reward : **{evaluation.challenge.coins}** {Emoji.coin}"
                        ),
                    )
                    if result == "OK"
                    else discord.Embed(
                        color=COLOR.red,
                        description=(
                            f"{MESSAGE.failing}\n\nChallenge : **{evaluation.challenge.name}"
                            f"**\nLanguage : {evaluation.challenge.language}\nLevel : "
                            f"{evaluation.challenge.level}\nResult : **{result}**"
                        ),
                    )
                )
            )
        except Exception as e:
            print(f"Failed to send a message to {evaluation.user.name}\nError: {e}")

        print(
            log("Task", clr.green, "Evaluation", f"{evaluation.challenge.name} Done!")
        )

    EvaluationData.clear()
