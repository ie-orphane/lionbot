import discord
import random
from cogs import Cog


class Random(Cog):
    @discord.app_commands.command(description="Randomly choose geeks from a role.")
    @discord.app_commands.guild_only()
    @discord.app_commands.default_permissions(administrator=True)
    @discord.app_commands.describe(
        role="The role to choose from.",
        private="Whether to send the result privately.",
        count="The number of geeks to choose.",
    )
    async def random(
        self,
        interaction: discord.Interaction,
        role: discord.Role = None,
        count: int = 1,
        private: bool = True,
    ):
        await interaction.response.defer(ephemeral=private)
        self.cog_interaction(interaction, role=role, count=count, private=private)

        members = [
            member
            for member in (role.members if role else interaction.guild.members)
            if not member.bot
        ]

        geeks = random.sample(members, min(count, len(members)))

        if len(geeks) == 0:
            await interaction.followup.send(
                embed=discord.Embed(
                    color=self.color.red,
                    description=f"**Uh oh!** No geeks found in {role.mention}. 😢",
                ),
                ephemeral=private,
            )
            return

        await interaction.followup.send(
            content=(
                f">>> "
                + "\n".join([f"{i}. {geek.mention}" for i, geek in enumerate(geeks, 1)])
            ),
            ephemeral=private,
        )


async def setup(bot):
    await bot.add_cog(Random(bot))
