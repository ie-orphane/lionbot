import discord
from consts import COLOR
import re
from io import BytesIO
import requests
from datetime import datetime, UTC
from config import get_emoji
from models import ProductData, UserData
from utils import number, on_error


__all__ = ["ProductReView", "ProductBuyBtn", "ProductBuyView"]


class ProductModal(discord.ui.Modal, title="Feedback"):
    feedback = discord.ui.TextInput(
        label="What is the issue with this product?",
        style=discord.TextStyle.long,
        placeholder="Type your feedback here...",
        min_length=41,
        max_length=199,
    )

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        original = await interaction.original_response()
        embed = original.embeds[0]

        _id = None
        if (match := re.search(r"`([^`]+)`", embed.description)) is not None:
            _id = match.group(1)

        if _id is None:
            raise ValueError("Failed to get product ID.")

        if (product := ProductData.read(_id)) is None:
            raise ValueError("Failed to get product data.")

        if (
            user := await interaction.guild.fetch_member(product.author_id)
        ) is not None:
            try:
                await user.send(
                    embed=discord.Embed(
                        color=COLOR.red,
                        description=(
                            f"Unfortunately, your product **{product.name}** has been denied. ❌\n\n"
                            f"**Reason:**\n```\n{self.feedback.value}\n```\n\n"
                        ),
                    )
                    .set_footer(
                        text="Please review the feedback, make the necessary changes, and feel free to resubmit it."
                    )
                    .set_thumbnail(url=product.image)
                )
            except discord.Forbidden:
                pass

        product.feedback = self.feedback.value
        product.status = "denied"
        product.denied_at = str(datetime.now(UTC))
        product.update()

        embed.color = COLOR.red
        embed.description = (
            embed.description.replace("Pending ⏳", f"Denied {get_emoji('no', '❌')}")
            + f"\n**Feedback:** {self.feedback.value}"
        )
        await original.edit(embed=embed, view=None)

        await interaction.followup.send(
            embed=discord.Embed(
                color=COLOR.red,
                description=(
                    f"The product **{product.name}** has been denied. ❌\n\n"
                    f"**Feedback:**\n```\n{self.feedback.value}\n```"
                ),
            ),
            ephemeral=True,
        )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        return await on_error(self, interaction, error, "product:modal")


class ProductBuyBtn(
    discord.ui.DynamicItem[discord.ui.Button], template=r"(?P<id>[0-9a-zA-Z]+)"
):
    def __init__(self, _id: str) -> None:
        super().__init__(discord.ui.Button(custom_id=f"{_id}", label="💸 Buy"))
        self.id = _id

    @classmethod
    async def from_custom_id(
        cls,
        interaction: discord.Interaction,
        button: discord.ui.Button,
        match: re.Match[str],
        /,
    ):
        return cls(match["id"])

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)

        if (user := UserData.read(interaction.user.id)) is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=COLOR.red,
                    description=(
                        f"✋ {interaction.user.mention}, \n"
                        + "you need to register before buying this product.\n"
                        + "Use the `/register` command."
                    ),
                ),
                ephemeral=True,
            )
            return

        product: ProductData = ProductData.read(self.id)

        if product.buyers is not None and user.id in product.buyers:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=COLOR.red,
                    description=(
                        f"🫣 {interaction.user.mention},\n"
                        f"You've already bought **{product.name}**."
                    ),
                ),
                ephemeral=True,
            )
            return

        if product is None or product.status != "approved":
            await interaction.followup.send(
                embed=discord.Embed(
                    color=COLOR.red,
                    description=f"😔 {interaction.user.mention},\n**{product.name}** is no longer available.",
                ),
                ephemeral=True,
            )
            return

        if user.coins < product.price:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=COLOR.red,
                    description=(
                        f"😔 {interaction.user.mention},\n"
                        f"You need {number(product.price - user.coins)} more {get_emoji('coin')} to buy **{product.name}**."
                    ),
                ),
                ephemeral=True,
            )
            return

        product.buy(user)

        original = await interaction.original_response()
        if re.search(r"Sales: `(\d+)`", original.content):
            await original.edit(
                content=re.sub(
                    r"Sales: `(\d+)`",
                    f"Sales: `{len(product.buyers)}`",
                    original.content,
                )
            )
        else:
            lines = original.content.split("\n")
            lines.insert(-1, f"Sales: `{len(product.buyers)}`")
            await original.edit(content="\n".join(lines))

        if (
            user := await interaction.guild.fetch_member(product.author_id)
        ) is not None:
            try:
                await user.send(
                    embed=discord.Embed(
                        color=COLOR.yellow,
                        description=(
                            f"Great news! Someone has just bought your product **{product.name}**! 🎉\n\n"
                        ),
                    )
                    .set_footer(
                        text="Thank you for being a part of our marketplace! We look forward to your continued success!"
                    )
                    .set_thumbnail(url=product.image)
                )
            except discord.Forbidden:
                pass

        await interaction.followup.send(
            embed=discord.Embed(
                color=COLOR.green,
                description=(
                    f"🎉 {interaction.user.mention},\n"
                    f"You've successfully bought **{product.name}** for {number(product.price)} {get_emoji('coin')}."
                ),
            ).set_thumbnail(url=product.image),
            ephemeral=True,
        )


class ProductBuyView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot: discord.ext.commands.Bot = bot

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        item: discord.ui.Button | discord.ui.Select,
    ):
        return await on_error(self, interaction, error, item.custom_id)


class ProductReView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot: discord.ext.commands.Bot = bot

    @discord.ui.button(
        emoji=get_emoji("yes", None), label="Approve", custom_id="product:btn:approve"
    )
    async def approve(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer(ephemeral=True)

        original = await interaction.original_response()
        embed = original.embeds[0]

        _id = None
        if (match := re.search(r"`([^`]+)`", embed.description)) is not None:
            _id = match.group(1)

        if _id is None:
            raise Exception("Failed to get product ID.")

        if (product := ProductData.read(_id)) is None:
            raise Exception("Failed to get product data.")

        channel: discord.ForumChannel = self.bot.get_listed_channel(
            channel_name="shop", is_text_channel=False
        )
        if channel is None:
            raise Exception("Shop channel not found")

        product.status = "approved"
        product.approved_at = str(datetime.now(UTC))
        product.update()

        embed.color = COLOR.green
        embed.description = embed.description.replace(
            "Pending ⏳", f"Approved {get_emoji('yes', '✅')}"
        )
        await original.edit(embed=embed, view=None)

        message = ""
        if product.description is not None:
            message = f"{product.description}\n"
        message += (
            f"Price: {number(product.price)} {get_emoji('coin')}\n"
            f"By: {product.author.mention} ({product.author.name})"
        )

        file = discord.utils.MISSING
        if product.image is not None:
            response = requests.get(product.image)
            if response.status_code == 200:
                file = discord.File(
                    BytesIO(response.content), filename=f"{product.name}.png"
                )

        await channel.create_thread(
            name=f"{product.name}",
            content=message,
            view=ProductBuyView(self.bot).add_item(ProductBuyBtn(product.id)),
            file=file,
        )

        if (
            user := await interaction.guild.fetch_member(product.author_id)
        ) is not None:
            try:
                await user.send(
                    embed=discord.Embed(
                        color=COLOR.green,
                        description=(
                            f"Good news 🤩!\n**{product.name}** has been successfully approved! ✅\n"
                            "It is now ready to be listed in the shop for purchase."
                        ),
                    ).set_footer(
                        text="Thank you for your submission, and we hope it performs well in the shop!"
                    )
                )
            except discord.Forbidden:
                pass

        await interaction.followup.send(
            embed=discord.Embed(
                color=COLOR.green,
                description=(
                    f"The product **{product.name}** has been successfully approved! ✅\n\n"
                    "It is now ready to be listed in the shop for purchase. "
                ),
            ),
            ephemeral=True,
        )

    @discord.ui.button(
        emoji=get_emoji("no", None), label="Deny", custom_id="product:btn:deny"
    )
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ProductModal(self.bot))

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        item: discord.ui.Button | discord.ui.Select,
    ):
        return await on_error(self, interaction, error, item.custom_id)
