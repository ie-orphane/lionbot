import discord
from discord.ext import commands
from models import ClassData, StudentData
from utils import color
import random


@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
class Class(commands.GroupCog, name="class"):
    @discord.app_commands.command(name="add", description="add new class")
    @discord.app_commands.describe(name="the name of the class")
    async def add_class_command(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer()

        new_class = ClassData.read(name.lower())
        if new_class is not None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=color.red,
                    description=f"class **{name}** already exists",
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
                description=f"class **{name}** created succefully!",
            ),
            ephemeral=True,
        )

    @discord.app_commands.command(name="delete", description="delete a class")
    @discord.app_commands.describe(name="the name of the class")
    async def delete_class_command(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer()

        new_class = ClassData.read(name.lower())
        if new_class is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=color.red,
                    description=f"class **{name}** not found!",
                ),
                ephemeral=True,
            )
            return

        for role in interaction.guild.roles:
            if role.name == name.lower():
                await role.delete()
        new_class.delete()

        await interaction.followup.send(
            embed=discord.Embed(
                colour=color.green,
                description=f"class **{name}** deleted succefully!",
            ),
        )

    @discord.app_commands.command(name="assign", description="assign to a class")
    @discord.app_commands.describe(name="the class to assign to")
    async def assign_class_command(
        self, interaction: discord.Interaction, name: discord.Role
    ):
        await interaction.response.defer()

        current_class = ClassData.read(name.name.lower())
        if current_class is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=color.red,
                    description=f"class **{name.name}** not found!",
                ),
                ephemeral=True,
            )
            return

        student_user = StudentData.read(interaction.user.id)
        if student_user is None:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=color.red,
                    description=f"You're not regitred yet!",
                ).set_footer(text="Try /register"),
                ephemeral=True,
            )
            return

        if student_user in current_class.students:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=color.red,
                    description=f"You're already there!",
                ),
                ephemeral=True,
            )
            return

        await interaction.user.add_roles(name)
        current_class.students.append(student_user)
        current_class.update()

        await interaction.followup.send(
            embed=discord.Embed(
                color=color.green,
                description=f"You added to **{current_class.id}**!",
            ),
            ephemeral=True,
        )

    @discord.app_commands.command(
        name="unassign", description="unassign student from a class"
    )
    @discord.app_commands.describe(
        name="the name of the class", student="student to unassign"
    )
    async def unassign_class_command(
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
        if student_user is None or student_user not in current_class.students:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=color.red,
                    description=f"{student.mention} not found!",
                ),
                ephemeral=True,
            )
            return

        current_class.students.remove(student_user)
        current_class.update()

        await interaction.followup.send(
            embed=discord.Embed(
                color=color.green,
                description=f"{student.mention} removed from **{current_class.id}**!",
            ),
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Class(bot))
