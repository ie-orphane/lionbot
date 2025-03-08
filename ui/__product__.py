import discord
from consts import COLOR
import traceback
import env
import re
from io import BytesIO
import requests
from datetime import datetime, UTC
from config import get_emoji
from models import ProductData, UserData
from utils import number


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
                    f"Product Denied!\n\n**Feedback:**\n{self.feedback.value}"
                ),
            ),
            ephemeral=True,
        )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        log_id = int(datetime.now(UTC).timestamp())
        log_dir = f"{env.BASE_DIR}/storage/errors"
        with open(f"{log_dir}/{log_id}.log", "w") as file:
            file.writelines(
                [
                    f"User: {interaction.user.display_name} ({interaction.user.id})\n",
                    f"Interaction: product:modal ({interaction.id})\n",
                    f"Server: {interaction.guild} #{interaction.channel}\n",
                    f"Error: {error}\n",
                ]
            )
            traceback.print_exc(file=file)

        await interaction.followup.send(
            embed=discord.Embed(
                color=COLOR.red,
                description=(
                    "**Oops!** The bot sometimes takes a nap. 💤\n"
                    "Don't worry, we'll fix the issue as soon as possible!\n\n"
                    f"📝 **Error ID:** `{log_id}`"
                ),
            ).set_footer(
                text="If this error occurs multiple times, please contact the owner."
            )
        )

        if (error_channel := self.bot.get_listed_channel("error")) is None:
            return

        await error_channel.send(
            embed=discord.Embed(
                color=COLOR.red,
                description=(
                    f"User: {interaction.user.mention} ({interaction.user.id})\n"
                    f"Interaction: ProductModal ({interaction.id})\n"
                    f"Server: {interaction.guild} #{interaction.channel}\n"
                    f"Log: `{log_id}`\n"
                    f"Error: {error}\n"
                    f"```\n{traceback.format_exc()}\n```"
                ),
            )
        )


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
        if re.search(r"Purchases: `(\d+)`", original.content):
            await original.edit(
                content=re.sub(
                    r"Purchases: `(\d+)`",
                    f"Purchases: `{len(product.buyers)}`",
                    original.content,
                )
            )
        else:
            lines = original.content.split("\n")
            lines.insert(-1, f"Purchases: `{len(product.buyers)}`")
            await original.edit(content="\n".join(lines))

        await interaction.followup.send(
            embed=discord.Embed(
                color=COLOR.green,
                description=(
                    f"🎉 {interaction.user.mention},\n"
                    f"You've successfully bought **{product.name}** for {number(product.price)} {get_emoji('coin')}."
                ),
            ),
            ephemeral=True,
        )


class ProductBuyView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        product: discord.ui.Button,
    ) -> None:
        log_id = int(datetime.now(UTC).timestamp())
        log_dir = f"{env.BASE_DIR}/storage/errors"
        with open(f"{log_dir}/{log_id}.log", "w") as file:
            file.writelines(
                [
                    f"User: {interaction.user.display_name} ({interaction.user.id})\n",
                    f"Interaction: {product.custom_id} ({interaction.id})\n",
                    f"Server: {interaction.guild} #{interaction.channel}\n",
                    f"Error: {error}\n",
                ]
            )
            traceback.print_exc(file=file)

        await interaction.followup.send(
            embed=discord.Embed(
                color=COLOR.red,
                description=(
                    "**Oops!** The bot sometimes takes a nap. 💤\n"
                    "Don't worry, we'll fix the issue as soon as possible!\n\n"
                    f"📝 **Error ID:** `{log_id}`"
                ),
            ).set_footer(
                text="If this error occurs multiple times, please contact the owner."
            )
        )

        if (error_channel := self.bot.get_listed_channel("error")) is None:
            return

        await error_channel.send(
            embed=discord.Embed(
                color=COLOR.red,
                description=(
                    f"User: {interaction.user.mention} ({interaction.user.id})\n"
                    f"Interaction: {product.custom_id} ({interaction.id})\n"
                    f"Server: {interaction.guild} #{interaction.channel}\n"
                    f"Log: `{log_id}`\n"
                    f"Error: {error}\n"
                    f"```\n{traceback.format_exc()}\n```"
                ),
            )
        )


class ProductReView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

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

        await interaction.followup.send(
            embed=discord.Embed(
                color=COLOR.green,
                description="Product Approved!",
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
        product: discord.ui.Button,
    ) -> None:
        log_id = int(datetime.now(UTC).timestamp())
        log_dir = f"{env.BASE_DIR}/storage/errors"
        with open(f"{log_dir}/{log_id}.log", "w") as file:
            file.writelines(
                [
                    f"User: {interaction.user.display_name} ({interaction.user.id})\n",
                    f"Interaction: {product.custom_id} ({interaction.id})\n",
                    f"Server: {interaction.guild} #{interaction.channel}\n",
                    f"Error: {error}\n",
                ]
            )
            traceback.print_exc(file=file)

        await interaction.followup.send(
            embed=discord.Embed(
                color=COLOR.red,
                description=(
                    "**Oops!** The bot sometimes takes a nap. 💤\n"
                    "Don't worry, we'll fix the issue as soon as possible!\n\n"
                    f"📝 **Error ID:** `{log_id}`"
                ),
            ).set_footer(
                text="If this error occurs multiple times, please contact the owner."
            )
        )

        if (error_channel := self.bot.get_listed_channel("error")) is None:
            return

        await error_channel.send(
            embed=discord.Embed(
                color=COLOR.red,
                description=(
                    f"User: {interaction.user.mention} ({interaction.user.id})\n"
                    f"Interaction: {product.custom_id} ({interaction.id})\n"
                    f"Server: {interaction.guild} #{interaction.channel}\n"
                    f"Log: `{log_id}`\n"
                    f"Error: {error}\n"
                    f"```\n{traceback.format_exc()}\n```"
                ),
            )
        )
