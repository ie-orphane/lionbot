import discord
from discord.ext import commands

from cogs import GroupCog
from config import del_user, get_emblem, set_user
from notations import EMBLEM


@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
class Emblem(GroupCog, name="emblem"):
    @discord.app_commands.command(description="Award an emblem to a geek.")
    @discord.app_commands.describe(
        name="The name of the emblem.", geek="The geek to award the emblem to."
    )
    async def award(
        self, interaction: discord.Interaction, name: EMBLEM, geek: discord.Member
    ):
        await interaction.response.defer()
        self.cog_interaction(interaction, name=name, geek=geek)

        if await self.bot.user_is_unkown(interaction, geek) is None:
            return
        if not_error := set_user(geek.id, name):
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.green,
                    title="✅ Emblem awarded!",
                    description=(
                        f"Hooray {geek.mention}!\n"
                        f"The **{name}** {get_emblem(name)} emblem is now yours."
                    ),
                ).set_footer(text="Wear it with pride! 🎉"),
            )
            return
        if not_error is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    title="❌ Not found!",
                    description=f"**{name}** emblem not found.",
                ),
                ephemeral=True,
            )
            return
        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.red,
                title="❌ Already awarded!",
                description=f"{geek.mention} already has **{name}** {get_emblem(name)} emblem.",
            ),
            ephemeral=True,
        )

    @discord.app_commands.command(description="Revoke an emblem from a geek.")
    @discord.app_commands.describe(
        name="The name of the emblem.", geek="The geek to revoke the emblem from."
    )
    async def revoke(
        self, interaction: discord.Interaction, name: EMBLEM, geek: discord.Member
    ):
        await interaction.response.defer()
        self.cog_interaction(interaction, name=name, geek=geek)

        if await self.bot.user_is_unkown(interaction, geek) is None:
            return
        if not_error := del_user(geek.id, name):
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.green,
                    title="✅ Emblem revoked!",
                    description=(
                        "Oops!\n"
                        f"{geek.mention} has lost their **{name}** {get_emblem(name)} emblem."
                    ),
                ).set_footer(text="Don't worry, you can earn it back! 💪"),
            )
            return
        if not_error is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    title="❌ Not found!",
                    description=f"**{name}** emblem not found.",
                ),
                ephemeral=True,
            )
            return
        await interaction.followup.send(
            embed=discord.Embed(
                color=self.color.red,
                title="❌ Not awarded!",
                description=f"{geek.mention} doesn't have **{name}** {get_emblem(name)} emblem.",
            ),
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Emblem(bot))
