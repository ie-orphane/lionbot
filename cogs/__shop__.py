import discord
import re
from discord.ext import commands
from config import get_emoji
from utils import number
from cogs import GroupCog
from models import ItemData
from consts import COLOR
from ui import ItemReView


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
        _name="Item's name",
        _description="Item's description",
        price="Item's price",
        image="Item's image",
    )
    @discord.app_commands.rename(_name="name", _description="description")
    async def add(
        self,
        interaction: discord.Interaction,
        _name: discord.app_commands.Range[str, 3, 11],
        price: int,
        _description: discord.app_commands.Range[str, 11, 97],
        image: discord.Attachment = None,
    ):
        await interaction.response.defer(ephemeral=True)

        if (user := await self.bot.user_is_unkown(interaction)) is None:
            return

        name = re.sub(r"\s+", " ", _name).strip()
        description = re.sub(r"\s+", " ", _description).strip()

        if (
            await self.check(
                interaction,
                price <= 0,
                f"**{price}** is an invalid price!",
                "It must be greater than 0.",
            )
            or await self.check(
                interaction,
                11 < len(name) < 3,
                f"**{name}** is an invalid name!",
                "It must be between 3 and 11 characters.",
            )
            or await self.check(
                interaction,
                97 < len(description) < 11,
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

        item = ItemData.create(name, price, user.id, description)
        if image is not None:
            if image.content_type is None or not image.content_type.startswith(
                "image/"
            ):
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="❌ Submission failed",
                        color=COLOR.red,
                        description=(
                            f"{interaction.user.mention},\n"
                            + f"**{image.filename}** is an invalid file!\n"
                            + (
                                f"`{image.content_type.split(";")[0].split('/')[-1]}` is not a supported type 🚫"
                                if image.content_type is not None
                                else "It has an unknown type 🚫."
                            )
                        ),
                    ).set_footer(text="It must be an image."),
                    ephemeral=True,
                )
                return
            item.image = image.url
            item.update()

        await channel.send(
            embed=discord.Embed(
                color=COLOR.orange,
                title="📦 New Submission",
                description=(
                    f"**ID**: `{item.id}`\n"
                    f"**Name**: {item.name}\n"
                    f"**Price**: {number(item.price)} {get_emoji('coin')}\n"
                    f"**Description**: {item.description}\n"
                    f"**Author**: {interaction.user.mention} ({item.author.name})\n"
                    f"**Status**: Pending ⏳"
                ),
            ).set_image(url=item.image),
            view=ItemReView(self.bot),
        )

        embed = (
            discord.Embed(
                color=self.color.green,
                title="✅ Submission Succeeded",
                description=(
                    f"{interaction.user.mention}, item sent for review! 🕵️\n\n"
                    f"**ID**: `{item.id}`\n"
                    f"**Name**: {item.name}\n"
                    f"**Price**: {number(item.price)} {get_emoji('coin')}\n"
                    f"**Description**: {item.description}"
                ),
            )
            .set_footer(text="Please be patient. ⏳")
            .set_image(url=item.image)
        )

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Shop(bot))
