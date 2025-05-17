import re
from typing import Any, Coroutine

import discord
from discord.ext import commands

from cogs import GroupCog
from config import get_emoji
from consts import COLOR, INLIST_AMOUNT, OUTLIST_AMOUNT
from models import ProductData
from ui import ProductReView, ThelistView
from utils import number


@discord.app_commands.dm_only()
class Shop(GroupCog, name="shop"):
    async def __error(
        self,
        interaction: discord.Interaction,
        /,
        *desc: tuple[str],
        foot: str = None,
    ) -> Coroutine[Any, Any, None]:
        """
        Send an error interaction to the user.
        Args:
            interaction (discord.Interaction): The interaction containing the command.
            desc (tuple[str]): The error description.
        """
        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.red,
                title="❌ Submission failed!",
                description=f"✋ {interaction.user.mention},\n" + "\n".join(desc),
            ).set_footer(text=foot),
            ephemeral=True,
        )

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
        _name: discord.app_commands.Range[str, 5, 13],
        price: discord.app_commands.Range[int, 1],
        _description: discord.app_commands.Range[str, 17, 101],
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

        if (channel := self.bot.get_listed_channel("approve")) is None:
            return await self.__error(
                interaction,
                "the approval channel is not set up yet! 🫣",
                foot="Please contact the owner.",
            )

        product = ProductData.create(name, price, user.id, description, image.filename)
        if image is not None:
            if image.content_type is None or not image.content_type.startswith(
                "image/"
            ):
                return await self.__error(
                    interaction,
                    f"**{image.filename}** is an invalid file!",
                    (
                        f"`{image.content_type.split(";")[0].split('/')[-1]}` is not a supported type 🚫"
                        if image.content_type is not None
                        else "It has an unknown type 🚫."
                    ),
                    foot="It must be an image.",
                )
            if (image.size / (2**20)) > 1:
                return await self.__error(
                    interaction,
                    f"**{image.filename}** is too large! 🚫",
                    f"It must be less than or equal 1 MB.",
                )
            await image.save(product.image.path)

        embed = discord.Embed(
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
        )

        embed.set_image(url=product.image.url)

        await channel.send(
            embed=embed, file=product.image.file, view=ProductReView(self.bot)
        )

        embed.color = self.color.green
        embed.title = "✅ Submission Succeeded"
        embed.description = (
            f"{interaction.user.mention}, product sent for review! 🕵️\n\n"
            f"**ID**: `{product.id}`\n"
            f"**Name**: {product.name}\n"
            f"**Price**: {number(product.price)} {get_emoji('coin')}\n"
            f"**Description**: {product.description}"
        )
        embed.set_footer(text="Please be patient. ⏳")

        await interaction.followup.send(embed=embed, file=product.image.file)


@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
class _Shop(GroupCog, name="__shop"):
    @discord.app_commands.command(description="d")
    async def add(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        self.cog_interaction(interaction)

        channel: discord.ForumChannel = self.bot.get_listed_channel(
            channel_name="shop", is_text_channel=False
        )
        if channel is None:
            raise Exception("Shop channel not found")

        await channel.create_thread(
            name=f"The List",
            content=(
                f"A way for escaping or joining the **list**.\n\n**`Prices`**:\n"
                f"{get_emoji('empty')}- in: {number(INLIST_AMOUNT)} {get_emoji('coin')}\n"
                f"{get_emoji('empty')}- out: {number(OUTLIST_AMOUNT)} {get_emoji('coin')}\n"
                f"\n**`By`**: {self.bot.user.mention} (LionBot)"
            ),
            view=ThelistView(self.bot),
        )

        await interaction.followup.send(
            embed=discord.Embed(
                color=COLOR.green,
                description=(f"**The List** has been added to the shop! ✅"),
            ),
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Shop(bot))
    await bot.add_cog(_Shop(bot))
