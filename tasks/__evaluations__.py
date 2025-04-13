import subprocess
from datetime import UTC, datetime

import discord
from discord.ext import commands, tasks

from config import get_emoji
from consts import COLOR, MESSAGE
from models import EvaluationData
from utils import Log, number


@tasks.loop(minutes=1)
async def evaluations(bot: commands.Bot):
    for evaluation in EvaluationData.read_all():
        Log.job(
            "Evaluation", f"{evaluation.challenge.name} from {evaluation.user.name}"
        )

        feedback = None
        result = "OK"

        with open(evaluation.solution.path) as f:
            solution = f.read()

        forbiddens = set(
            evaluation.challenge.forbidden + evaluation.challenge.not_allowed
        ).intersection(solution.split())

        if len(forbiddens) > 0:
            result = "FORBIDDEN"
            print(f"\033[33mForbidden : {', '.join(forbiddens)}\033[0m")

        if result == "OK":
            for index, test in enumerate(evaluation.challenge.tests, 1):
                try:
                    completed_process = subprocess.run(
                        [evaluation.challenge.runner, evaluation.solution.path]
                        + test.args,
                        capture_output=True,
                        text=True,
                        timeout=4,
                    )
                except subprocess.TimeoutExpired:
                    result = "TIMEOUT"
                    print(
                        "\033[33m"
                        + " ".join(
                            ["Timeout :", evaluation.challenge.file]
                            + ['""' if arg == "" else arg for arg in test.args]
                        )
                        + "\033[0m"
                    )
                    break

                if completed_process.stderr:
                    feedback = (
                        " ".join(
                            [
                                "\033[1;31m$>",
                                evaluation.challenge.runner,
                                evaluation.challenge.file,
                            ]
                            + test.args
                        )
                        + f"\033[0m\t\n{completed_process.stderr}"
                    )
                    result = "ERROR"
                    print(
                        "\033[31m"
                        + " ".join(
                            ["Error :", evaluation.challenge.file]
                            + ['""' if arg == "" else arg for arg in test.args]
                        )
                        + "\033[0m"
                    )
                    print(f"{completed_process.stderr}")
                    break

                if completed_process.stdout != test.expected:
                    feedback = (
                        " ".join(
                            [
                                "\033[1;31m$>",
                                evaluation.challenge.runner,
                                evaluation.challenge.file,
                            ]
                            + test.args
                        )
                        + f"\033[0m\t\n{completed_process.stdout}"
                    )
                    result = "KO"
                    print(f"\u274c [{index}] {test.description}")
                    print(
                        " ".join(
                            ["$", evaluation.challenge.file]
                            + ['""' if arg == "" else arg for arg in test.args]
                        )
                    )

                    print(
                        "Expected \033[32m{}\033[0m got \033[31m{}\033[0m".format(
                            test.expected, completed_process.stdout
                        ).replace("\n", "\\n")
                    )
                    break

                print(f"\u2705 [{index}] {test.description}")

            if result == "OK":
                evaluation.user.add_coins(
                    evaluation.challenge.coins, "challenge reward"
                )

        evaluation.user._challenge.update(
            {
                "evaluated": str(datetime.now(UTC)),
                "_solution": evaluation.solution.filename,
                "result": result,
            }
        )

        evaluation.user._log = None
        if feedback is not None:
            evaluation.user._log = {
                "language": evaluation.challenge.language,
                "id": evaluation.challenge.id,
                "name": evaluation.challenge.name,
                "attempt": evaluation.user.challenge.attempt,
                "trace": feedback,
                "cost": evaluation.challenge.coins * 0.05,
                "result": result,
            }

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
                            f"{MESSAGE.succeeding}\n\n"
                            f"**`Challenge`**: **{evaluation.challenge.name}**\n"
                            f"**`Language`**: {evaluation.challenge.language} {get_emoji(evaluation.challenge.language)}\n"
                            f"**`Level`**: {evaluation.challenge.level}\n"
                            f"**`Result`**: **{result}**\n"
                            f"**`Reward`**: {number(evaluation.challenge.coins)} {get_emoji("coin")}"
                        ),
                    )
                    if result == "OK"
                    else discord.Embed(
                        color=COLOR.red,
                        description=(
                            f"{MESSAGE.failing}\n\n"
                            f"**`Challenge`**: **{evaluation.challenge.name}**\n"
                            f"**`Language`**: {evaluation.challenge.language} {get_emoji(evaluation.challenge.language)}\n"
                            f"**`Level`**: {evaluation.challenge.level}\n"
                            f"**`Result`**: **{result}**"
                        ),
                    )
                )
            )
        except Exception as e:
            print(f"Failed to send a message to {evaluation.user.name}\nError: {e}")

        Log.job("Evaluation", f"{evaluation.challenge.name} Done!")

        evaluation.remove()
