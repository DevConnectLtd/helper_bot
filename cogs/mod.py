from __future__ import annotations

import typing

import disnake
from disnake.ext import commands

from core.bot import HelperBot
from core.constants import RoleID, ChannelID
from core.models import WarnData
from core.utils import HelperCog
from pages.warn_pag import WarnPaginator


class Moderation(HelperCog):
    """Moderation commands"""

    @commands.command("ban")
    @commands.has_role(RoleID.MODERATOR)
    async def ban(
        self,
        ctx: commands.Context[HelperBot],
        member: disnake.Member,
        clean_history_duration: int = 0,
        *,
        reason: str = "No reason provided",
    ) -> None:
        await member.ban(clean_history_duration=clean_history_duration, reason=reason)
        await ctx.reply(f"`{member}` banned successfully with the reason {reason}")
        log_embed = disnake.Embed(
            title=f"{ctx.author} banned {member}",
            description=(f"{member} ({member.id}) was banned by " f"{ctx.author} with the reason __{reason}__."),
            color=disnake.Color.red(),
            timestamp=disnake.utils.utcnow(),
        ).set_thumbnail(url=member.display_avatar)
        await self._log_action(log_embed)

    @commands.command("kick")
    @commands.has_role(RoleID.MODERATOR)
    async def kick(
        self, ctx: commands.Context[HelperBot], member: disnake.Member, *, reason: str = "No reason provided"
    ) -> None:
        await member.kick(reason=reason)
        await ctx.reply(f"`{member}` was kicked successfully with the reason {reason}")
        log_embed = disnake.Embed(
            title=f"{ctx.author} kicked {member}",
            description=(f"{member} ({member.id}) was kicked by " f"{ctx.author} with the reason __{reason}__."),
            color=disnake.Color.yellow(),
            timestamp=disnake.utils.utcnow(),
        ).set_thumbnail(url=member.display_avatar)
        await self._log_action(log_embed)

    @commands.command("unban")
    @commands.has_role(RoleID.MODERATOR)
    async def unban(self, ctx: commands.GuildContext, member_id: int, *, reason: str = "No reason provided") -> None:
        try:
            await ctx.guild.unban(disnake.Object(member_id), reason=reason)
            await ctx.reply(f"`{member_id}` was unbanned successfully with the reason {reason}")
            log_embed = disnake.Embed(
                title=f"{ctx.author} unbanned {member_id}",
                description=(f"{member_id} was unbanned by " f"{ctx.author} with the reason __{reason}__."),
                color=disnake.Color.green(),
                timestamp=disnake.utils.utcnow(),
            )
            await self._log_action(log_embed)
        except disnake.HTTPException:
            await ctx.reply(
                "Unban failed. Peraphs is the `member_id` that you're passing not valid? "
                "If you think that this is an error pleas contact one of the developers."
            )

    async def _log_action(self, embed: disnake.Embed) -> None:
        channel = await self.bot.fetch_channel(ChannelID.MODERATION_LOG_CHANNEL_ID)
        channel = typing.cast(disnake.TextChannel, channel)
        await channel.send(embed=embed)

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

        log_embed = disnake.Embed(
            title=f"{ctx.author} warned {member}",
            description=(f"{member} ({member.id}) was warned by " f"{ctx.author} with the reason __{reason}__."),
            color=disnake.Color.teal(),
            timestamp=disnake.utils.utcnow(),
        ).set_thumbnail(url=member.display_avatar)
        await self._log_action(log_embed)

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
        warn_data = WarnData(**data)  # type: ignore
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
