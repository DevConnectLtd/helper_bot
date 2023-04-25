from __future__ import annotations

import datetime
import typing

import disnake
from disnake.ext import commands

if typing.TYPE_CHECKING:
    from core.bot import HelperBot
    from core.utils import HelperCog


class BotHelp(commands.HelpCommand):
    context: commands.Context[HelperBot]

    @staticmethod
    def command_list(cog: HelperCog) -> list[str]:
        command_data: list[str] = []
        for command in cog.get_commands():  # type: ignore
            command: commands.Command | commands.Group  # type: ignore
            if isinstance(command, commands.Group):
                command_data.extend(map(lambda a: a.qualified_name, command.commands))  # type: ignore
            else:
                command_data.append(command.name)
        return command_data

    async def send_bot_help(self, _mapping: typing.Any):
        embed = disnake.Embed(
            color=disnake.Color.purple(), description=self.context.bot.description, timestamp=datetime.datetime.now()
        ).set_author(name="DevConnect Help", icon_url=self.context.bot.user.display_avatar)
        for cog in filter(lambda a: not a.hidden, self.context.bot.cogs.values()):
            embed.add_field(
                cog.qualified_name,
                f"*{cog.description}*\n`{'`, `'.join(self.command_list(cog))}`",  # type: ignore
                inline=False,
            )
        await self.context.reply(embed=embed)
