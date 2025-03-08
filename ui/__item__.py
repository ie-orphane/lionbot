import discord
from consts import COLOR
import traceback
import env
import re
from datetime import datetime, UTC
from config import get_emoji
from models import ItemData, UserData
from utils import number


__all__ = ["ItemReView", "ItemBuyBtn", "ItemBuyView"]


class ItemModal(discord.ui.Modal, title="Feedback"):
    feedback = discord.ui.TextInput(
        label="What do you think is wrong about this item?",
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
            raise ValueError("Failed to get item ID.")

        if (item := ItemData.read(_id)) is None:
            raise ValueError("Failed to get item data.")

        item.feedback = self.feedback.value
        item.status = "denied"
        item.denied_at = str(datetime.now(UTC))
        item.update()

        embed.color = COLOR.red
        embed.description = (
            embed.description.replace("Pending ⏳", f"Denied {get_emoji('no', '❌')}")
            + f"\n**Feedback:** {self.feedback.value}"
        )
        await original.edit(embed=embed, view=None)

        await interaction.followup.send(
            embed=discord.Embed(
                color=COLOR.red,
                description=(f"Item Denied!\n\n**Feedback:**\n{self.feedback.value}"),
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
                    f"Interaction: item:modal ({interaction.id})\n",
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
                    f"Interaction: ItemModal ({interaction.id})\n"
                    f"Server: {interaction.guild} #{interaction.channel}\n"
                    f"Log: `{log_id}`\n"
                    f"Error: {error}\n"
                    f"```\n{traceback.format_exc()}\n```"
                ),
            )
        )


class ItemBuyBtn(
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
                        + "you need to register before buying this item.\n"
                        + "Use the `/register` command."
                    ),
                ),
                ephemeral=True,
            )
            return

        item: ItemData = ItemData.read(self.id)

        if item.buyers is not None and user.id in item.buyers:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=COLOR.red,
                    description=(
                        f"🫣 {interaction.user.mention},\n"
                        f"You've already bought **{item.name}**."
                    ),
                ),
                ephemeral=True,
            )
            return

        if item is None or item.status != "approved":
            await interaction.followup.send(
                embed=discord.Embed(
                    color=COLOR.red,
                    description=f"😔 {interaction.user.mention},\n**{item.name}** is no longer available.",
                ),
                ephemeral=True,
            )
            return

        if user.coins < item.price:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=COLOR.red,
                    description=(
                        f"😔 {interaction.user.mention},\n"
                        f"You need {number(item.price - user.coins)} more {get_emoji('coin')} to buy **{item.name}**."
                    ),
                ),
                ephemeral=True,
            )
            return

        item.buy(user)

        original = await interaction.original_response()
        if re.search(r"Purchases: `(\d+)`", original.content):
            await original.edit(
                content=re.sub(
                    r"Purchases: `(\d+)`",
                    f"Purchases: `{len(item.buyers)}`",
                    original.content,
                )
            )
        else:
            lines = original.content.split("\n")
            lines.insert(-1, f"Purchases: `{len(item.buyers)}`")
            await original.edit(content="\n".join(lines))

        await interaction.followup.send(
            embed=discord.Embed(
                color=COLOR.green,
                description=(
                    f"🎉 {interaction.user.mention},\n"
                    f"You've successfully bought **{item.name}** for {number(item.price)} {get_emoji('coin')}."
                ),
            ),
            ephemeral=True,
        )


class ItemBuyView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        item: discord.ui.Button,
    ) -> None:
        log_id = int(datetime.now(UTC).timestamp())
        log_dir = f"{env.BASE_DIR}/storage/errors"
        with open(f"{log_dir}/{log_id}.log", "w") as file:
            file.writelines(
                [
                    f"User: {interaction.user.display_name} ({interaction.user.id})\n",
                    f"Interaction: {item.custom_id} ({interaction.id})\n",
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
                    f"Interaction: {item.custom_id} ({interaction.id})\n"
                    f"Server: {interaction.guild} #{interaction.channel}\n"
                    f"Log: `{log_id}`\n"
                    f"Error: {error}\n"
                    f"```\n{traceback.format_exc()}\n```"
                ),
            )
        )


class ItemReView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(
        emoji=get_emoji("yes", None), label="Approve", custom_id="item:btn:approve"
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
            raise Exception("Failed to get item ID.")

        if (item := ItemData.read(_id)) is None:
            raise Exception("Failed to get item data.")

        channel: discord.ForumChannel = self.bot.get_listed_channel(
            channel_name="shop", is_text_channel=False
        )
        if channel is None:
            raise Exception("Shop channel not found")

        item.status = "approved"
        item.approved_at = str(datetime.now(UTC))
        item.update()

        embed.color = COLOR.green
        embed.description = embed.description.replace(
            "Pending ⏳", f"Approved {get_emoji('yes', '✅')}"
        )
        await original.edit(embed=embed, view=None)

        message = ""
        if item.description is not None:
            message = f"{item.description}\n"
        message += (
            f"Price: {number(item.price)} {get_emoji('coin')}\n"
            f"By: {item.author.mention} ({item.author.name})"
        )

        await channel.create_thread(
            name=f"{item.name}",
            content=message,
            view=ItemBuyView(self.bot).add_item(ItemBuyBtn(item.id)),
        )

        await interaction.followup.send(
            embed=discord.Embed(
                color=COLOR.green,
                description="Item Approved!",
            ),
            ephemeral=True,
        )

    @discord.ui.button(
        emoji=get_emoji("no", None), label="Deny", custom_id="item:btn:deny"
    )
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ItemModal(self.bot))

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        item: discord.ui.Button,
    ) -> None:
        log_id = int(datetime.now(UTC).timestamp())
        log_dir = f"{env.BASE_DIR}/storage/errors"
        with open(f"{log_dir}/{log_id}.log", "w") as file:
            file.writelines(
                [
                    f"User: {interaction.user.display_name} ({interaction.user.id})\n",
                    f"Interaction: {item.custom_id} ({interaction.id})\n",
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
                    f"Interaction: {item.custom_id} ({interaction.id})\n"
                    f"Server: {interaction.guild} #{interaction.channel}\n"
                    f"Log: `{log_id}`\n"
                    f"Error: {error}\n"
                    f"```\n{traceback.format_exc()}\n```"
                ),
            )
        )
