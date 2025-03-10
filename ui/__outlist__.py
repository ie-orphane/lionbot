import discord
import env
from config import get_emoji
from utils import get_week, open_file, number, on_error
import datetime as dt
from consts import COLOR
from zoneinfo import ZoneInfo


class OutlistView(discord.ui.View):
    color = COLOR

    def __init__(self, bot, timeout: float):
        super().__init__(timeout=timeout)
        self.bot = bot

    async def on_timeout(self):
        message: discord.Message
        this_week = get_week()
        weeks = open_file(f"{env.BASE_DIR}/data/outlist.json")
        current_week = weeks.get(str(this_week.count))

        if (
            ((message_id := (current_week.get("message_id"))) is None)
            or ((channel := self.bot.get_listed_channel("events")) is None)
            or ((message := await channel.fetch_message(message_id)) is None)
        ):
            return

        await message.edit(
            view=None, content=message.content.replace("Started", "Ended")
        )

    @discord.ui.button(label="🏃 out")
    async def out(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        if (user := await self.bot.user_is_unkown(interaction)) is None:
            return

        black_list_role = None

        for role in interaction.guild.roles:
            if role.name == "Black List":
                black_list_role = role

        if (
            black_list_role is None
            or interaction.user.get_role(black_list_role.id) is None
        ):
            if user.greylist:
                await interaction.user.add_roles(black_list_role)
                user.greylist = False
                user.update()
                await interaction.followup.send(
                    embed=discord.Embed(
                        color=self.color.yellow,
                        description=(
                            f"{interaction.user.mention}, 🥳.\nCongrats for joining the {black_list_role}.\n"
                        ),
                    ),
                    ephemeral=True,
                )
                return

            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, 🤔.\nWe can't find you in {black_list_role}.",
                ).set_footer(text="wanna join it?"),
                ephemeral=True,
            )
            user.greylist = True
            user.update()
            return

        this_week = get_week()
        weeks = open_file(f"{env.BASE_DIR}/data/outlist.json")
        current_week = weeks.get(str(this_week.count))

        if not (
            not (current_week is None)
            and (current_week["claimed_by"] is None)
            and dt.datetime.fromisoformat(current_week["started_at"])
            <= dt.datetime.now(ZoneInfo("Africa/Casablanca")).replace(
                second=0, microsecond=0
            )
            <= dt.datetime.fromisoformat(current_week["started_at"])
            + dt.timedelta(seconds=current_week["ends_in"])
        ):
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, ⏰.\nThe event already finished.",
                ).set_footer(text="maybe next week!"),
                ephemeral=True,
            )
            return

        if user.coins < current_week["amount"]:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, 😔.\nYou need {number(current_week["amount"] - user.coins)} {get_emoji("coin")} more.",
                ),
                ephemeral=True,
            )
            return

        await interaction.user.remove_roles(black_list_role)

        current_week["claimed_by"] = interaction.user.id
        open_file(f"{env.BASE_DIR}/data/outlist.json", weeks)

        user.greylist = False
        user.sub_coins(current_week["amount"], "outlist event")

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                description=f"{interaction.user.mention}, congarts 🥳!\nYou paied {number(current_week["amount"])} {get_emoji("coin")}",
            ).set_footer(text="you're free now."),
            ephemeral=True,
        )

        button.disabled = True
        original = await interaction.original_response()
        embed = original.embeds[0]
        embed.description += f"\n\n**Escaper(s)**:\n- {interaction.user.mention}"

        await original.edit(embed=original.embeds[0], view=self)

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        item: discord.ui.Button | discord.ui.Select,
    ):
        return await on_error(self, interaction, error, item.custom_id)
