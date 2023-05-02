from __future__ import annotations

import typing

import disnake
from disnake.ext import commands

from core.bot import HelperBot
from core.constants import RoleID
from core.models import WarnData
from core.utils import HelperCog
from pages.warn_pag import WarnPaginator


class Moderation(HelperCog):
    """Moderation commands"""

    @commands.group("warn", description="warn actions", invoke_without_command=True)
    @commands.has_role(RoleID.MODERATOR)
    async def warn(
        self, ctx: commands.Context[HelperBot], member: disnake.Member, *, reason: str = "No reason provided"
    ) -> None:
        warns = await ctx.bot.db.add_warn(ctx.author.id, member.id, reason)
        await ctx.reply(
            embed=ctx.bot.generic_embed(ctx, f"Warned (#{warns}) `{member}` | {reason}").set_footer(
                text=f"By: {ctx.author}"
            )
        )

    @warn.command("case", description="Displays info about a particular warn case by it's ID")
    @commands.has_role(RoleID.MODERATOR)
    async def case(self, ctx: commands.Context[HelperBot], id: int) -> None:
        data: dict[str, typing.Any] | None = await ctx.bot.pool.fetchrow(  # type: ignore
            "SELECT * FROM devconnect_warns WHERE id = $1", id
        )
        if data is None:
            await ctx.reply(
                embed=ctx.bot.generic_embed(ctx, f"No warn case with ID {id} exists.", color=disnake.Color.red())
            )
            return
        warn_data = WarnData(**data) # type: ignore
        await ctx.reply(
            embed=ctx.bot.generic_embed(ctx, warn_data.reason)
            .add_field("Target", warn_data.user_id)
            .add_field("Target", f"{ctx.bot.get_user(warn_data.user_id)} ({warn_data.user_id})", inline=False)
            .add_field("Moderator", f"{ctx.bot.get_user(warn_data.mod_id)} ({warn_data.mod_id})", inline=False)
            .set_author(name=f"Warn #{id}")
        )

    @warn.command("info", description="check warn info related to a user")
    @commands.has_role(RoleID.MODERATOR)
    async def info(self, ctx: commands.Context[HelperBot], *, user: disnake.User | None) -> None:
        user_id = (user.id if user else None) or ctx.author.id
        warns = await ctx.bot.pool.fetch("SELECT * FROM devconnect_warns WHERE user_id = $1", user_id)  # type: ignore
        if not warns:
            await ctx.reply(embed=ctx.bot.generic_embed(ctx, "User has no warnings"))
            return
        pag = WarnPaginator(ctx, map(lambda d: WarnData(**d), warns))  # type: ignore
        pag.message = await ctx.reply(embed=pag.prepare_embed(), view=pag)
