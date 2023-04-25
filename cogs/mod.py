from __future__ import annotations

import typing

import disnake
from disnake.ext import commands

from core.bot import HelperBot
from core.constants import RoleID
from core.models import WarnData
from core.utils import HelperCog


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
    async def case(self, ctx: commands.Context[HelperBot], id: int) -> None:
        data: dict[str, typing.Any] | None = await ctx.bot.pool.fetchrow(  # type: ignore
            "SELECT * FROM devconnect_warns WHERE id = $1", id
        )
        if data is None:
            await ctx.reply(
                embed=ctx.bot.generic_embed(ctx, f"No warn case with ID {id} exists.", color=disnake.Color.red())
            )
            return
        warn_data = WarnData(**data)
        await ctx.reply(
            embed=ctx.bot.generic_embed(ctx, warn_data.reason)
            .add_field("Target", warn_data.user_id)
            .add_field("Moderator", warn_data.mod_id)
            .add_field("Created on:", disnake.utils.format_dt(warn_data.created_at, "R"), inline=False)
            .set_author(name=f"Warn #{id}")
        )
