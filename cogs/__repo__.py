import re
import env
import discord
import requests
from discord.ext import commands
from constants import COLOR
from urllib.parse import urlparse
from config import set_message


def check_git_link(link: str) -> tuple[bool, str, str]:
    tokens = urlparse(link)
    is_valid_link = all(
        getattr(tokens, qualifying_attr) for qualifying_attr in ("scheme", "netloc")
    )
    username, reponame = None, None

    if is_valid_link:
        if tokens.netloc == "github.com" and (
            match := re.search(r"github\.com/([^/]+)/([^/]+)", link)
        ):
            username, reponame = match.groups()
    elif link.count("/") >= 1:
        username, reponame, *_ = link.split("/")

    if (not username) or (not reponame):
        return False, None, None

    response = requests.get(
        url=f"https://api.github.com/repos/{username}/{reponame}",
        headers={"Authentication": f"Bearer {env.GITHUB_ACCESS_TOKEN}"},
    )

    if not response.ok:
        return False, None, None

    return True, username, reponame


@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
class Repo(commands.GroupCog, name="repo"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.color = COLOR

    @discord.app_commands.command(description="add a new repository to the log")
    @discord.app_commands.describe(link="the repository link")
    async def add(self, interaction: discord.Interaction, link: str):
        await interaction.response.defer()

        is_valid, username, repo_name = check_git_link(link)

        if not is_valid:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"Oops! The repository link '**{link}**' maybe invalid !",
                )
            )
            return

        set_message("GITLOG", f"{username}/{repo_name}", None)

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                description=f"[{repo_name}](https://github.com/{username}/{repo_name}) repository added succefuly",
            ),
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Repo(bot))
