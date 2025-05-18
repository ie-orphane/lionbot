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

    async def __check(
        self, interaction: discord.Interaction, check: bool, body: str, foot: str
    ) -> bool:
        if check:
            await self.__error(
                interaction,
                body,
                foot=foot,
            )
        return check

    @discord.app_commands.command(description="Add new product in the shop.")
    @discord.app_commands.describe(
        _name="Product's name",
        price="Product's price",
        _description="Product's description",
        image="Product's image",
        source="Product's source",
    )
    @discord.app_commands.rename(_name="name", _description="description")
    async def add(
        self,
        interaction: discord.Interaction,
        _name: discord.app_commands.Range[str, 5, 23],
        price: discord.app_commands.Range[int, 1],
        _description: discord.app_commands.Range[str, 17, 101],
        image: discord.Attachment = None,
        source: discord.Attachment = None,
    ):
        await interaction.response.defer()
        self.cog_interaction(
            interaction, name=_name, price=price, description=_description, image=image
        )

        if (user := await self.bot.user_is_unkown(interaction)) is None:
            return

        name = re.sub(r"\s+", " ", _name).strip()
        description = re.sub(r"\s+", " ", _description).strip()

        if await self.__check(
            interaction,
            23 < len(name) < 3,
            f"**{name}** is an invalid name! 🚫",
            "It must be between 3 and 23 characters.",
        ) or await self.__check(
            interaction,
            97 < len(description) < 11,
            f"**{description}** is an invalid description! 🚫",
            "It must be between 11 and 97 characters.",
        ):
            return

        if (channel := self.bot.get_listed_channel("approve")) is None:
            return await self.__error(
                interaction,
                "the approval channel is not set up yet! 🫣",
                foot="Please contact the owner.",
            )

        if (image is not None) and (
            image.content_type is None or not image.content_type.startswith("image/")
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
        if (image is not None) and ((image.size / (2**20)) > 1):
            return await self.__error(
                interaction,
                f"**{image.filename}** is too large! 🚫",
                f"It must be less than or equal 1 MB.",
            )
        if (source is not None) and ((source.size / (2**20)) > 1):
            return await self.__error(
                interaction,
                f"**{source.filename}** is too large! 🚫",
                f"It must be less than or equal 1 MB.",
            )

        product = ProductData.create(
            name,
            price,
            user.id,
            description,
            None if image is None else image.filename,
            None if source is None else source.filename,
        )

        if image is not None:
            await image.save(product.image.path)
        if source is not None:
            await source.save(product.source.path)

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
            embed=embed,
            content=(
                f"Source: **{product.source.filename}**"
                if product._source is not None
                else None
            ),
            files=[
                file
                for file in (product.source.file, product.image.file)
                if file is not discord.utils.MISSING
            ],
            view=ProductReView(self.bot),
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
