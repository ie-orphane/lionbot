import discord
from discord.ext import commands
from models import ClassData, StudentData
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

    @discord.app_commands.command(name="delete", description="delete a class")
    @discord.app_commands.default_permissions(administrator=True)
    @discord.app_commands.guild_only()
    @discord.app_commands.describe(name="the name of the class")
    async def delete_class_command(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer()

        new_class = ClassData.read(name.lower())
        if new_class is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=color.red,
                    description=f"class {name} not found!",
                ),
                ephemeral=True,
            )
            return

        for role in interaction.guild.roles:
            if role.name == name.lower():
                role.delete()
        new_class.delete()

        await interaction.followup.send(
            embed=discord.Embed(
                colour=color.green,
                description=f"class {name} deleted succefully!",
            ),
        )

    @discord.app_commands.command(name="assign", description="assign user to a class")
    @discord.app_commands.default_permissions(administrator=True)
    @discord.app_commands.guild_only()
    @discord.app_commands.describe(name="the name of the class")
    async def assign_class_command(
        self, interaction: discord.Interaction, name: str, student: discord.Member
    ):
        await interaction.response.defer()

        current_class = ClassData.read(name.lower())
        if current_class is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=color.red,
                    description=f"class **{name}** not found!",
                ),
                ephemeral=True,
            )
            return

        student_user = StudentData.read(student.id)
        if student_user is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=color.red,
                    description=f"{student.mention} not regitred yet!",
                ),
                ephemeral=True,
            )
            return
        
        if student_user in current_class.students:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=color.red,
                    description=f"{student.mention} already there!",
                ),
                ephemeral=True,
            )
            return

        current_class.add_student(student_user)
        await interaction.followup.send(
            embed=discord.Embed(
                color=color.green,
                description=f"user {student.mention} added to {current_class.id}!",
            ),
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Class(bot))
