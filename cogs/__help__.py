import discord
from cogs import Cog
from typing import Literal
from config import get_user, get_config, get_emoji


class Help(Cog):
    @discord.app_commands.guild_only()
    @discord.app_commands.command(description="List all bot commands.")
    async def help(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.cog_interaction(interaction)

        commands = await self.bot.tree.fetch_commands()
        embed = (
            discord.Embed(
                color=self.color.yellow,
                description=f"{self.bot.user.display_name} is a tool built to help you track your stats and improve your coding skills.\n\n\n ",
            )
            .set_author(
                name=f"Salam {interaction.user.display_name} !",
                icon_url=interaction.user.avatar.url,
            )
            .set_footer(text="Also try >help")
        )

        categories: dict[
            Literal["challenge", "general"],
            list[
                discord.app_commands.AppCommand | discord.app_commands.AppCommandGroup
            ],
        ] = {
            "general": (":globe_with_meridians: General", []),
            "set": (":lock: Data", []),
            "project": ("💼 Project", []),
        }

        for command in commands:
            if command.name in ["help", "challenge", "shop"]:
                continue

            is_group = False
            is_admin_only = False

            if not (command.default_member_permissions is None):
                for (
                    permission_name,
                    has_permission,
                ) in command.default_member_permissions:
                    if permission_name == "administrator" and has_permission:
                        is_admin_only = True

            if is_admin_only:
                continue

            for option in command.options:
                if isinstance(option, discord.app_commands.AppCommandGroup):
                    is_group = True
                    categories[
                        command.name if command.name in categories else "general"
                    ][1].append(option)

            if command.name == "register":
                categories["set"][1].append(command)
                continue

            if not is_group:
                categories["general"][1].append(command)

        for index, (_, (category_title, commands)) in enumerate(categories.items(), 1):
            embed.add_field(
                name=category_title,
                value="\n\n".join(
                    [
                        f"{command.mention}\n{command.description}"
                        for command in commands
                    ]
                ),
                inline=index != len(categories),
            )

        if (not ((owner_id := get_user("owner")) is None)) and (
            not ((owner := self.bot.get_user(owner_id)) is None)
        ):
            embed.add_field(
                name="Developed by", value=f"{get_emoji("owner")} {owner.mention}"
            )

        if not ((repo_link := get_config("REPOSITORY")) is None):
            embed.add_field(
                name="Repository link",
                value=f"[{get_emoji("github")} /repo]({repo_link})",
            )

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Help(bot))
