from __future__ import annotations

import typing

import disnake
from disnake.ext import commands

if typing.TYPE_CHECKING:
    from core.bot import HelperBot


class ErrorHandlerImpl:
    async def on_command_error(self, ctx: commands.Context[HelperBot], exception: Exception) -> None:
        if not isinstance(exception, commands.CommandOnCooldown):
            ctx.command.reset_cooldown(ctx)  # type: ignore
        if isinstance(exception, commands.CommandNotFound):
            return
        elif isinstance(exception, (commands.MemberNotFound, commands.UserNotFound)):
            text = f"Member/User `{exception.argument}` was not found."
        elif isinstance(exception, commands.CommandOnCooldown):
            text = f"Hold on mate! Wait {round(exception.retry_after)} more seconds before you run the command again."
        elif isinstance(exception, commands.MissingPermissions):
            mising_perms = "\n".join(f"`{perm}`" for perm in exception.missing_permissions)
            text = f"Looks like you don't have following permission(s) to run this command.\n{mising_perms}"
        elif isinstance(exception, commands.MissingRole):
            text = f"Looks like you don't have following role to run this command.\nRole ID: `{exception.missing_role}`"
        elif isinstance(exception, commands.MissingRequiredArgument):
            missing_arg = (str(exception.param).split(":"))[0]
            text = f"You are missing following required argument to run this command.\n`{missing_arg}`"
        else:
            raise exception
        await ctx.reply(embed=ctx.bot.generic_embed(ctx, text, color=disnake.Color.red()))
