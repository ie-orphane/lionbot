import os
import discord
import requests
from dotenv import load_dotenv
from discord import TextChannel
from discord.ext import tasks, commands
from utils import Log
from config import get_channel
from models import UserData
from datetime import datetime
from constants import COLOR
from config import get_message, set_message


GITHUB_API_URL = "https://api.github.com"
GITHUB_REPO_NAME = "casatourat-backend"


@tasks.loop(minutes=2)
async def gitlog(bot: commands.Bot):
    load_dotenv()
    GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")

    if GITHUB_ACCESS_TOKEN is None:
        Log.error("GitLog", ".env missed GITHUB_ACCESS_TOKEN")
        return

    if (gitlog_channel_id := get_channel("gitlog")) is None:
        Log.error("GitLog", "channel id not found")
        return

    if (gitlog_channel := bot.get_channel(gitlog_channel_id)) is None:
        Log.error("GitLog", "channel not found")
        return

    if not isinstance(gitlog_channel, TextChannel):
        Log.error("GitLog", "channel is not a TextChannel")
        return

    headers = {"Authentication": f"Bearer {GITHUB_ACCESS_TOKEN}"}

    response = requests.get(
        url=f"{GITHUB_API_URL}/repos/forkanimahdi/{GITHUB_REPO_NAME}", headers=headers
    )

    if response.status_code != 200:
        Log.error("GitLog", f"request failed with code {response.status_code}")
        return

    repo = response.json()

    repo_updated_at = int(
        datetime.fromisoformat(repo.get("created_at", "2023-10-23T00:00Z")).timestamp()
    )
    repo_created_at = int(
        datetime.fromisoformat(repo.get("updated_at", "2023-10-23T00:00Z")).timestamp()
    )

    embed = discord.Embed(
        color=COLOR.yellow,
        description=(
            f"visibility: {repo.get("visibility", "")}\n"
            f"created at: <t:{repo_created_at}:D> <t:{repo_created_at}:R>\n"
            f"updated at: <t:{repo_updated_at}:D> <t:{repo_updated_at}:R>\n"
        ),
    ).set_author(name=repo.get("name", ""), url=repo.get("html_url"))

    if (repo_contributors_url := repo.get("contributors_url")) is None:
        print("cannot get contributs url")
        return

    response = requests.get(url=repo_contributors_url, headers=headers)

    if response.status_code != 200:
        print("failed to get repository contributes")
        return

    repo_contributors = {}
    repo_contributions_count = 0
    max_len = 0

    for repo_contributor in response.json():

        repo_contributions_count += repo_contributor.get("contributions", 0)

        repo_contributions = repo_contributor.get("contributions", 0)

        max_len = max(len(str(repo_contributions)), max_len)

        repo_contributors[repo_contributor.get("html_url")] = {
            "contributions": repo_contributions,
            "login": repo_contributor.get("login", ""),
        }

    for user in UserData.read_all():
        if (repo_contributor := repo_contributors.get(user.socials.github)) is None:
            continue

        repo_contributor["id"] = user.id

    embed.description += f"contributions: {repo_contributions_count}\n\n"
    embed.description += "\n".join(
        [
            (
                f"`{contributor['contributions']:>{max_len}}`  |  [{contributor['login']}]({contributor_url})"
                f"{"" if contributor.get('id') is None else f" <@{contributor.get('id')}>"}"
            )
            for contributor_url, contributor in repo_contributors.items()
        ]
    )

    if (message_id := get_message("GITLOG", GITHUB_REPO_NAME)) is not None:
        try:
            message = await gitlog_channel.fetch_message(message_id)
            await message.edit(content="", embeds=[embed])
            return
        except discord.NotFound:
            pass
    else:
        Log.warning("GitLog", f"{GITHUB_REPO_NAME} message id not found")

    message = await gitlog_channel.send(content="", embeds=[embed])

    set_message("GITLOG", GITHUB_REPO_NAME, message.id)
