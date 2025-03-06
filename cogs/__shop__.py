import discord
import re
from discord.ext import commands
from config import get_emoji
from utils import number
from cogs import GroupCog
from models import ItemData
from consts import COLOR


@discord.app_commands.guild_only()
class Shop(GroupCog, name="shop"):
    @staticmethod
    async def check(
        interaction: discord.Interaction, check: bool, body: str, foot: str
    ) -> bool:
        if check:
            await interaction.followup.send(
                embed=discord.Embed(
                    title="❌ Submission failed",
                    color=COLOR.red,
                    description=f"{interaction.user.mention}, {body} 🚫",
                ).set_footer(text=foot),
                ephemeral=True,
            )
        return check

    @discord.app_commands.command(description="Add new item in the shop.")
    @discord.app_commands.describe(
        _title="Item's title", _description="Item's description", price="Item's price"
    )
    @discord.app_commands.rename(_title="title", _description="description")
    async def add(
        self,
        interaction: discord.Interaction,
        _title: discord.app_commands.Range[str, 3, 11],
        price: int,
        _description: discord.app_commands.Range[str, 11, 97] = None,
    ):
        await interaction.response.defer(ephemeral=True)

        if (user := await self.bot.user_is_unkown(interaction)) is None:
            return

        title = re.sub(r"\s+", " ", _title).strip()
        description = (
            re.sub(r"\s+", " ", _description).strip()
            if _description is not None
            else None
        )

        if (
            await self.check(
                interaction,
                price <= 0,
                f"**{price}** is an invalid price!",
                "It must be greater than 0.",
            )
            or await self.check(
                interaction,
                11 < len(title) < 3,
                f"**{title}** is an invalid title!",
                "It must be between 3 and 11 characters.",
            )
            or await self.check(
                interaction,
                description is not None and 97 < len(description) < 11,
                f"**{description}** is an invalid description!",
                "It must be between 11 and 97 characters.",
            )
        ):
            return

        if (channel := self.bot.get_listed_channel("approve")) is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    title="❌ Submission failed",
                    color=COLOR.red,
                    description=f"{interaction.user.mention}, approval channel not found! 🫣",
                ).set_footer(text="Please contact the owner."),
                ephemeral=True,
            )
            return

        item = ItemData.create(title, price, user.id, description)

        await channel.send(
            embed=discord.Embed(
                color=COLOR.blue,
                title="📦 New Submission",
                description=(
                    f"**ID**: `{item.id}`\n"
                    f"**Title**: {item.title}\n"
                    f"**Price**: {number(item.price)} {get_emoji('coin')}\n"
                    f"**Description**: {item.description or 'N/A'}\n"
                    f"**Author**: {interaction.user.mention}"
                ),
            )
        )

        embed = discord.Embed(
            color=self.color.green,
            title="✅ Submission Succeeded",
            description=(
                f"{interaction.user.mention}, item sent for review! 🕵️\n\n"
                f"Item information:\n"
                f"**ID**: `{item.id}`\n"
                f"**Title**: {item.title}\n"
                f"**Price**: {number(item.price)} {get_emoji('coin')}\n"
                f"**Description**: {item.description or 'N/A'}\n"
                f"**Author**: {interaction.user.mention}"
            ),
        ).set_footer(text="Please be patient. ⏳")

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Shop(bot))
