import json
import re
from pathlib import Path

import discord

import env
from consts import COLOR
from utils import month, on_error

__all__ = ["GiveawayView"]


class GiveawayView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="🎉", custom_id="giveaway:enter")
    async def enter(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        current = month.current()

        path = Path(env.BASE_DIR) / "data" / "giveaway.json"
        with open(path) as f:
            data = json.load(f)
        if current.id not in data:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=COLOR.red,
                    description=f"{interaction.user.mention} 🚫,\nthis giveaway has ended.",
                ),
                ephemeral=True,
            )
            return
        if interaction.user.id in data[current.id]["entrants"]:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=COLOR.red,
                    description=f"{interaction.user.mention} 🚫,\nyou are already entered in this giveaway!",
                ).set_footer(text="be patient."),
                ephemeral=True,
            )
            return
        data[current.id]["entrants"].append(interaction.user.id)

        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        await interaction.followup.send(
            embed=discord.Embed(
                color=COLOR.green,
                description=f"{interaction.user.mention} ✅,\nyou have successfully entered the giveaway!",
            ).set_footer(text="Good luck!"),
            ephemeral=True,
        )
        if (
            ((message_id := (data[current.id].get("message_id"))) is not None)
            and ((channel := interaction.channel) is not None)
            and ((message := await channel.fetch_message(message_id)) is not None)
        ):
            embed = message.embeds[0]
            embed.description = re.sub(
                r"Entrants: \*\*`(\d+)`\*\*",
                f"Entrants: **`{len(data[current.id]['entrants'])}`**",
                embed.description,
            )
            await message.edit(embed=embed, view=self)

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        item: discord.ui.Button | discord.ui.Select,
    ):
        return await on_error(self, interaction, error, item.custom_id)
