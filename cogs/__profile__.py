import discord

import env
from api import wakapi
from cogs import Cog
from config import get_emoji, get_user, get_users
from utils import number


class Profile(Cog):
    @discord.app_commands.guild_only()
    @discord.app_commands.command(description="View the basic geek information.")
    @discord.app_commands.describe(
        member="Choose a fellow geek.", private="View profile in private."
    )
    async def profile(
        self,
        interaction: discord.Interaction,
        member: discord.Member | discord.User = None,
        private: bool = True,
    ):
        await interaction.response.defer(ephemeral=private)
        self.cog_interaction(interaction, member=member)

        member = member or interaction.user

        if (
            await self.bot.user_is_self(interaction, member)
            or await self.bot.user_on_cooldown(
                interaction, interaction.command.qualified_name
            )
            or (await self.bot.user_is_admin(interaction, member))
            or (user := await self.bot.user_is_unkown(interaction, member)) is None
        ):
            return

        favorite_language = ""
        user._socials["wakatime"] = env.WAKATIME_BASE_URL

        if (
            not (user.token is None)
            and not (
                (user_data := await wakapi.get_stats(user.token, "all_time")) is None
            )
            and not ((user_data := user_data.get("data")) is None)
        ):
            user._socials["wakatime"] += f"/@{user_data.get('user_id', '')}"
            if languages := user_data.get("languages"):
                favorite_language = sorted(
                    languages, key=lambda x: x.get("total_seconds", 0)
                )[-1]

        embed = discord.Embed(color=self.color.yellow, description="").set_author(
            name=user.name, icon_url=member.avatar
        )

        if user.training and user.training.startswith("coding"):
            embed.description += f"\n`Class`: **Coding** - Web Development **{user.training.removeprefix("coding")}**"
        if favorite_language:
            embed.description += f"\n`Favorite Language`: {get_emoji(favorite_language['name'])} {favorite_language['name']}"

        embed.description += f"\n\n`Coins`: {number(user.coins)} {get_emoji("coin")}"
        emblems = []
        if user.id == get_user("owner"):
            emblems.append(get_emoji("owner", None))
        if user.id in get_users("admins"):
            emblems.append(get_emoji("admin", None))
        if user.id in get_users("coaches"):
            emblems.append(get_emoji("coach", None))
        emblems = [emblem for emblem in emblems if emblem is not None]
        if emblems:
            embed.description += "\n`Emblems`: " + "".join(emblems)

        embed.description += "\n\n`Socials`:\n" + "\n".join(
            [
                f"{get_emoji('empty')}[{get_emoji(social)}  {social}]({link})"
                for social, link in user.socials
                if link
            ]
        )

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Profile(bot))
