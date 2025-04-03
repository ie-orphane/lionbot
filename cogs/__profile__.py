import env
import discord
from cogs import Cog
from utils import number
from config import get_emoji
from api import wakapi


class Profile(Cog):
    @discord.app_commands.guild_only()
    @discord.app_commands.command(description="View the basic geek information.")
    @discord.app_commands.describe(member="Choose a fellow geek.")
    async def profile(
        self,
        interaction: discord.Interaction,
        member: discord.Member | discord.User = None,
    ):
        await interaction.response.defer()
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
