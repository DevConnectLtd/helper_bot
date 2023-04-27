from __future__ import annotations

import typing

import disnake
from disnake.ext import commands

if typing.TYPE_CHECKING:
    from core.bot import HelperBot


class ErrorHandlerImpl:
    async def on_command_error(self, ctx: commands.Context[HelperBot], exception: Exception) -> None:
        if isinstance(exception, commands.CommandNotFound):
            return
        elif isinstance(exception, (commands.MemberNotFound, commands.UserNotFound)):
            text = f"Member/User `{exception.argument}` was not found."

        else:
            raise exception
        await ctx.reply(embed=ctx.bot.generic_embed(ctx, text, color=disnake.Color.red()))
