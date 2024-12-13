import env
import discord
import requests
from discord.ext import tasks
from utils import Log
from models import UserData
from datetime import datetime, UTC
from constants import COLOR, GITHUB_API_URL
from config import set_message, get_config


@tasks.loop(minutes=7)
async def gitlog(bot):
    if (gitlog_channel := bot.get_listed_channel("gitlog")) is None:
        Log.error("Gitlog", "error while getting gitlog channel")
        return

    if (repo_msgs_id := get_config("GITLOG", "msgs")) is None:
        Log.error("Gitlog", "error while getting gitlog repositories")
        return

    for repo_name, message_id in repo_msgs_id.items():
        Log.job("Gitlog", f"{repo_name}")

        headers = {"Authentication": f"Bearer {env.GITHUB_ACCESS_TOKEN}"}
        print(headers)

        response = requests.get(
            url=f"{GITHUB_API_URL}/repos/forkanimahdi/{repo_name}", headers=headers
        )

        if response.status_code != 200:
            Log.error("GitLog", f"repository: {response.status_code} {response.text}")
            continue

        repo = response.json()

        repo_updated_at = int(
            datetime.fromisoformat(
                repo.get("created_at", "2023-10-23T00:00Z")
            ).timestamp()
        )
        repo_created_at = int(
            datetime.fromisoformat(
                repo.get("updated_at", "2023-10-23T00:00Z")
            ).timestamp()
        )

        embed = (
            discord.Embed(
                color=COLOR.yellow,
                description=(
                    f"visibility: {repo.get("visibility", "")}\n"
                    f"created at: <t:{repo_created_at}:D> <t:{repo_created_at}:R>\n"
                    f"updated at: <t:{repo_updated_at}:D> <t:{repo_updated_at}:R>\n"
                ),
            )
            .set_author(name=repo.get("name", ""), url=repo.get("html_url"))
            .set_footer(
                text=f"{datetime.now(UTC):%A  %d  %b   %I:%M  %p}".replace(
                    "AM", "am"
                ).replace("PM", "pm")
            )
        )

        if (repo_contributors_url := repo.get("contributors_url")) is None:
            Log.error("Gitlog", f"contributors url not found")
            continue

        response = requests.get(url=repo_contributors_url, headers=headers)

        if response.status_code != 200:
            Log.error(
                "GitLog",
                f"contributors: request failed with code {response.status_code}",
            )
            continue

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

        if message_id is not None:
            try:
                message = await gitlog_channel.fetch_message(message_id)
                await message.edit(content="", embeds=[embed])
                continue
            except discord.NotFound:
                pass
        else:
            Log.warning("GitLog", f"{repo_name} message id not found")

        message = await gitlog_channel.send(content="", embeds=[embed])

        set_message("GITLOG", repo_name, message.id)
