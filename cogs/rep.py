from __future__ import annotations

import disnake
from disnake.ext import commands

from core.bot import HelperBot
from core.utils import HelperCog
from core.constants import RoleID

import typing

class Reputation(HelperCog):
    """Reputation related commands."""

    @commands.group(name="rep", description="Reputation commands", invoke_without_command=True)
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    async def rep(self, ctx: commands.Context[HelperBot], member: disnake.Member) -> None:
        if ctx.author == member:
            await ctx.reply("You cannot rep for yourself!", delete_after=3.0)
            ctx.command.reset_cooldown(ctx) # type: ignore
            return
        elif member.bot:
            await ctx.reply("Sorry mate, You cannot rep for a bot.", delete_after=3.0)
            ctx.command.reset_cooldown(ctx) # type: ignore
            return
        total_reps = await ctx.bot.db.add_rep(member.id)
        await ctx.reply(
            embed=ctx.bot.generic_embed(ctx, f"Added +1 rep to **{str(member)}**. The user has {total_reps} reps now!", color=disnake.Color.green())
        )

    @rep.command(name="add", descriptions="Adds an amount of reps to a user.")
    @commands.has_role(RoleID.MODERATOR)
    async def add(self, ctx: commands.Context[HelperBot], member: disnake.Member, reps: int):
        if member.bot:
            await ctx.reply("Sorry mate, You cannot add rep(s) of a bot.", delete_after=3.0)
            return
        total_reps = await ctx.bot.db.add_rep(member.id, reps)
        await ctx.reply(
            embed=ctx.bot.generic_embed(ctx, f"Added +{reps} rep to **{str(member)}**. The user has {total_reps} reps now!", color=disnake.Color.green())
        )

    @rep.command(name="remove", description="Removes certin amount of reps from a user")
    @commands.has_role(RoleID.MODERATOR)
    async def remove(self, ctx: commands.Context[HelperBot], member: disnake.Member, reps: int) -> None:
        if member.bot:
            await ctx.reply("Sorry mate, You cannot remove rep(s) of a bot.", delete_after=3.0)
            return
        total_reps = await ctx.bot.db.remove_rep(member.id, reps)
        await ctx.reply(
            embed=ctx.bot.generic_embed(ctx, f"Removed {reps} rep of **{str(member)}**. The user has {total_reps} reps now!", color=disnake.Color.green())
        )
    
    @rep.command(name="info", description="Shows reputations of a specific user.")
    async def info(self, ctx: commands.Context[HelperBot], user: disnake.User | None) -> None:
        user_id = (user.id if user else None) or ctx.author.id
        data = await ctx.bot.pool.fetchval("SELECT reps FROM devconnect_reps WHERE user_id = $1", user_id) # type: ignore
        if not data:
            await ctx.reply("The user doesn't have any reputations yet.")
            return
        await ctx.reply(f"The user has **`{data}`** reps currently.")
    
    @rep.command(name="top", description="Shows the leaderboard of reputations", aliases=["lb", "leaderboard"])
    async def top(self, ctx: commands.Context[HelperBot]) -> None:
        data: typing.List[typing.Any] = await ctx.bot.pool.fetch("SELECT user_id, reps FROM devconnect_reps ORDER BY reps DESC") # type: ignore
        if len(data) == 0:
            await ctx.reply("No one in the leaderboard yet.")
            return
        leaderboard = ""
        for i, rep_data in enumerate(data):
            user = (ctx.bot.get_user(rep_data["user_id"]))
            leaderboard += f"{i+1}. **{str(user)}**: {rep_data['reps']}\n"
        await ctx.reply(embed=ctx.bot.generic_embed(ctx, leaderboard, title="Reputations Leaderboard",color=disnake.Color.green()))
