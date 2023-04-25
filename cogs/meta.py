from __future__ import annotations

from disnake.ext import commands

from core.bot import HelperBot
from core.utils import HelperCog


class Meta(HelperCog):
    """Command related to bot and it's stats."""

    @commands.command("ping", description="bot's latency")
    async def ping(self, ctx: commands.Context[HelperBot]) -> None:
        await ctx.reply(embed=self.bot.generic_embed(ctx, f"🏓 Ponag! `{ctx.bot.latency*1000:.2f}ms`"))
