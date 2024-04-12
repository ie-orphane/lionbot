import discord
from discord.ext import commands
from models import ClassData
from utils import color
import random


class Class(
    commands.GroupCog,
    name="class",
    group_name="class",
    description="class",
    group_description="class",
):
    @discord.app_commands.command(name="add", description="add new class")
    @discord.app_commands.default_permissions(administrator=True)
    @discord.app_commands.guild_only()
    @discord.app_commands.describe(name="the name of the class")
    async def add_class_command(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer()

        new_class = ClassData.read(name.lower())
        if new_class is not None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=color.red,
                    description=f"class {name} already exists",
                ),
                ephemeral=True,
            )
            return


        colour = random.choice(color.all)
        await interaction.guild.create_role(name=name, colour=colour)
        ClassData(id=name.lower(), students=[]).update()

        await interaction.followup.send(
            embed=discord.Embed(
                colour=colour,
                description=f"class {name} created succefully!",
            ),
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Class(bot))
