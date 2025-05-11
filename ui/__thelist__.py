import discord

from config import get_emoji
from consts import COLOR, INLIST_AMOUNT, OUTLIST_AMOUNT
from models import UserData
from utils import number, on_error

__all__ = ["ThelistView"]


class ThelistSelect(discord.ui.UserSelect):
    def __init__(self, bot):
        super().__init__(
            custom_id="thelist:in:select", placeholder="Choose the geek..."
        )
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        member = self.values[0]

        if (user := UserData.read(interaction.user.id)) is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=COLOR.red,
                    description=(
                        f"✋ {interaction.user.mention}, \n"
                        f"you need to register before using the `thelist:in`.\n"
                        "Instead, use the `/register` command."
                    ),
                ),
                ephemeral=True,
            )
            return

        black_list_role = None

        for role in interaction.guild.roles:
            if role.name == "Black List":
                black_list_role = role

        if black_list_role is None:
            await interaction.edit_original_response(
                embed=discord.Embed(
                    color=COLOR.red,
                    description=(
                        f"{interaction.user.mention}, 🤔.\n"
                        f"We can't find the **Black list**!"
                    ),
                ).set_footer(text="please contact a staff"),
                view=None,
            )
            return

        if member.bot:
            await interaction.edit_original_response(
                embed=discord.Embed(
                    color=COLOR.red,
                    description=(
                        f"{interaction.user.mention}, 🤔.\n"
                        f"{member.mention} has no place in {black_list_role.mention}.\n"
                    ),
                ),
                view=None,
            )
            return

        if member in black_list_role.members:
            await interaction.edit_original_response(
                embed=discord.Embed(
                    color=COLOR.red,
                    description=(
                        f"{interaction.user.mention}, 🤔.\n"
                        f"{member.mention} is already in {black_list_role.mention}."
                    ),
                ),
                view=None,
            )
            return

        if user.coins < INLIST_AMOUNT:
            await interaction.edit_original_response(
                embed=discord.Embed(
                    color=COLOR.red,
                    description=(
                        f"{interaction.user.mention}, 🤔.\nYou need {number(INLIST_AMOUNT - user.coins)} {get_emoji('coin')} more."
                    ),
                ),
                view=None,
            )
            return

        await member.add_roles(black_list_role)

        user.sub_coins(INLIST_AMOUNT, f"blacklist in {member.id}")

        await interaction.edit_original_response(
            embed=discord.Embed(
                color=COLOR.green,
                description=(
                    f"{interaction.user.mention}, 🥳!\n"
                    f"Congarts {member.mention}, he's now in the jail!\n"
                ),
            ),
            view=None,
        )


class ThelistView(discord.ui.View):
    color = COLOR

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="🔒 in", custom_id="thelist:in")
    async def in_(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        if UserData.read(interaction.user.id) is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=COLOR.red,
                    description=(
                        f"✋ {interaction.user.mention}, \n"
                        f"you need to register before using the `thelist:in`.\n"
                        "Instead, use the `/register` command."
                    ),
                ),
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            view=discord.ui.View().add_item(ThelistSelect(self.bot)), ephemeral=True
        )

    @discord.ui.button(label="🏃 out", custom_id="thelist:out")
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
                            f"{interaction.user.mention}, congrats for joining {black_list_role.mention}.\n"
                            f"To appeal 😔, you must pay {number(OUTLIST_AMOUNT)} {get_emoji('coin')}."
                        ),
                    ),
                    ephemeral=True,
                )
                return

            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, next time maybe 🤔.\nWe can't find you in {black_list_role.mention}.",
                ).set_footer(text="wanna join it?"),
                ephemeral=True,
            )
            user.greylist = True
            user.update()
            return

        if user.coins < OUTLIST_AMOUNT:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"{interaction.user.mention}, you need {number(OUTLIST_AMOUNT - user.coins)} {get_emoji("coin")} more.",
                ),
                ephemeral=True,
            )
            return

        await interaction.user.remove_roles(black_list_role)

        user.greylist = False
        user.sub_coins(OUTLIST_AMOUNT, "blacklist out")

        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.green,
                description=f"{interaction.user.mention}, congarts 🥳!\nYou paied {number(OUTLIST_AMOUNT)} {get_emoji("coin")}.",
            ).set_footer(text="you're free now."),
            ephemeral=True,
        )

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        item: discord.ui.Button | discord.ui.Select,
    ):
        return await on_error(self, interaction, error, item.custom_id)
