import discord
from models import UserData
from cogs import Cog
from constants import BOT_COINS_AMOUNT
from utils import number
from config import get_emoji, get_users, get_config
from api import wakapi
from env import WAKATIME_BASE_URL


class Profile(Cog):
    @discord.app_commands.guild_only()
    @discord.app_commands.command(description="view basic geek information.")
    @discord.app_commands.describe(member="choose a fellow member.")
    async def profile(
        self,
        interaction: discord.Interaction,
        member: discord.Member | discord.User = None,
    ):
        await interaction.response.defer()

        member = member or interaction.user

        if interaction.application_id == member.id:
            embed = (
                discord.Embed(
                    color=self.color.yellow,
                )
                .set_author(name=member.name, icon_url=member.avatar)
                .add_field(
                    name="Class",
                    value=f"> **Coding** - Discord Integration",
                    inline=False,
                )
                .add_field(
                    name="Coins",
                    value=f"> {number(BOT_COINS_AMOUNT)} {get_emoji("coin")}",
                    inline=False,
                )
                .add_field(
                    name="Favorite Language",
                    value=f"> {get_emoji("Python")}  Python",
                    inline=False,
                )
                .add_field(
                    name="Socials",
                    value=(
                        f"- [{get_emoji("github")}  github](https://github.com/ie-orphane/lionbot)\n"
                        f"- [{get_emoji("portfolio")}  portfolio](https://lionsgeek.ma/)"
                    ),
                )
            )

            await interaction.followup.send(embed=embed)
            return

        admins = get_users("owner", "coach", nullable=False)
        roles: set[discord.Role] = set()
        if not ((main_guild := self.bot.get_guild(get_config("GUILD"))) is None):
            roles = {
                role for role in main_guild.roles if role.name in get_config("ROLES")
            }
        if interaction.user != member and not (
            {role for role in interaction.user.roles} & roles
            or interaction.user.id in admins
        ):
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=(
                        f"{interaction.user.mention}, oops 🫣!\n"
                        f"You can't see {member.mention}'s profile.\n\n"
                        f"Only the following members can see other profiles:\n"
                        + "\n".join(
                            [
                                f"- {admin.mention}"
                                for admin in map(lambda x: self.bot.get_user(x), admins)
                                if admin
                            ]
                            + [f"- {role.mention}" for role in roles]
                        )
                    ),
                ),
                ephemeral=True,
            )
            return

        if (user := UserData.read(member.id)) is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{member.mention}{', you are' if member == interaction.user else ' is'} not registered yet!",
                ).set_footer(text="use /register instead"),
                ephemeral=True,
            )
            return

        favorite_language = ""
        user._socials["wakatime"] = WAKATIME_BASE_URL

        if (
            (user.token is not None)
            and (
                (user_data := await wakapi.get_stats(user.token, "all_time"))
                is not None
            )
            and ((user_data := user_data.get("data")) is not None)
        ):
            user._socials["wakatime"] += f"/@{user_data['user_id']}"
            if languages := user_data["languages"]:
                favorite_language = sorted(languages, key=lambda x: x["total_seconds"])[
                    -1
                ]

        embed = discord.Embed(
            color=self.color.yellow,
        ).set_author(name=user.name, icon_url=member.avatar)

        if user.training and user.training.startswith("coding"):
            embed.add_field(
                name="Class",
                value=f"> **Coding** - Web Development **{user.training.removeprefix("coding")}**",
                inline=False,
            )

        embed.add_field(
            name="Coins",
            value=f"> {number(user.coins)} {get_emoji("coin")}",
            inline=False,
        )

        if favorite_language:
            embed.add_field(
                name="Favorite Language",
                value=f"> {get_emoji(favorite_language['name'])} {favorite_language['name']}",
                inline=False,
            )

        embed.add_field(
            name="Socials",
            value="\n".join(
                [
                    f"- [{get_emoji(social)}  {social}]({link})"
                    for social, link in user.socials
                    if link
                ]
            ),
        )

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Profile(bot))
