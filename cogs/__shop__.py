import discord
import re
from discord.ext import commands
from config import get_emoji
from utils import number
from cogs import GroupCog
from models import ProductData
from consts import COLOR
from ui import ProductReView


@discord.app_commands.dm_only()
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

    @discord.app_commands.command(description="Add new product in the shop.")
    @discord.app_commands.describe(
        _name="Product's name",
        _description="Product's description",
        price="Product's price",
        image="Product's image",
    )
    @discord.app_commands.rename(_name="name", _description="description")
    async def add(
        self,
        interaction: discord.Interaction,
        _name: discord.app_commands.Range[str, 3, 11],
        price: discord.app_commands.Range[int, 1],
        _description: discord.app_commands.Range[str, 11, 97],
        image: discord.Attachment = None,
    ):
        await interaction.response.defer()
        self.cog_interaction(
            interaction, name=_name, price=price, description=_description, image=image
        )

        if (user := await self.bot.user_is_unkown(interaction)) is None:
            return

        name = re.sub(r"\s+", " ", _name).strip()
        description = re.sub(r"\s+", " ", _description).strip()

        if await self.check(
            interaction,
            11 < len(name) < 3,
            f"**{name}** is an invalid name!",
            "It must be between 3 and 11 characters.",
        ) or await self.check(
            interaction,
            97 < len(description) < 11,
            f"**{description}** is an invalid description!",
            "It must be between 11 and 97 characters.",
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

        product = ProductData.create(name, price, user.id, description)
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
            product.image = image.url
            product.update()

        await channel.send(
            embed=discord.Embed(
                color=COLOR.orange,
                title="📦 New Submission",
                description=(
                    f"**ID**: `{product.id}`\n"
                    f"**Name**: {product.name}\n"
                    f"**Price**: {number(product.price)} {get_emoji('coin')}\n"
                    f"**Description**: {product.description}\n"
                    f"**Author**: {interaction.user.mention} ({product.author.name})\n"
                    f"**Status**: Pending ⏳"
                ),
            ).set_image(url=product.image),
            view=ProductReView(self.bot),
        )

        embed = (
            discord.Embed(
                color=self.color.green,
                title="✅ Submission Succeeded",
                description=(
                    f"{interaction.user.mention}, product sent for review! 🕵️\n\n"
                    f"**ID**: `{product.id}`\n"
                    f"**Name**: {product.name}\n"
                    f"**Price**: {number(product.price)} {get_emoji('coin')}\n"
                    f"**Description**: {product.description}"
                ),
            )
            .set_footer(text="Please be patient. ⏳")
            .set_image(url=product.image)
        )

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Shop(bot))
