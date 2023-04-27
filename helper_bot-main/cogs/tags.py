from __future__ import annotations

from typing import Any

import disnake
from disnake.ext import commands

from core.bot import HelperBot
from core.models import TagData
from core.utils import HelperCog


class Tags(HelperCog):
    """Tag commands."""

    @commands.group("tag", description="Group handling tags.", aliases=["t"], invoke_without_command=True)
    async def tag(self, ctx: commands.Context[HelperBot], *, query: str | None = None) -> None:
        if query:
            await self.get(ctx, name=query)

    @tag.command("create", description="Creates a tag.", aliases=["add", "make"])
    async def create(self, ctx: commands.Context[HelperBot], name: str, *, content: str) -> None:
        tag: str | None = await ctx.bot.pool.fetchval(  # type: ignore
            "SELECT content FROM devconnect_tags WHERE name = $1", name.lower()
        )
        if tag is not None:
            await ctx.reply(
                embed=ctx.bot.generic_embed(ctx, f"Tag named `{name}` already exists.", color=disnake.Color.red())
            )
        await ctx.bot.db.add_tag(name, ctx.author.id, content)
        await ctx.reply(embed=ctx.bot.generic_embed(ctx, f"Tag with name `{name}` was created!"))

    @tag.command("get", description="displays a tag", aliases=["show", "display"])
    async def get(self, ctx: commands.Context[HelperBot], *, name: str) -> None:
        tag: str | None = await ctx.bot.pool.fetchval(  # type: ignore
            "SELECT content FROM devconnect_tags WHERE name = $1", name.lower()
        )
        if tag is None:
            await ctx.reply(embed=ctx.bot.generic_embed(ctx, f"No tag named `{name}` found", color=disnake.Color.red()))
            return
        to_reply = m.message_id if ((m := ctx.message.reference) and m.message_id) else ctx.message.id
        assert isinstance(tag, str)
        await ctx.channel.get_partial_message(to_reply).reply(  # type: ignore
            embed=ctx.bot.generic_embed(ctx, tag).set_author(name=name)
        )

    @tag.command("info", description="get information about a tag.")
    async def taginfo(self, ctx: commands.Context[HelperBot], *, name: str) -> None:
        tag: dict[str, Any] | None = await ctx.bot.pool.fetchrow(  # type: ignore
            "SELECT * FROM devconnect_tags WHERE name = $1", name.lower()
        )
        if tag is None:
            await ctx.reply(embed=ctx.bot.generic_embed(ctx, f"No tag named `{name}` found", color=disnake.Color.red()))
            return
        tag_data = TagData(**tag)
        await ctx.reply(
            embed=ctx.bot.generic_embed(ctx, f"Info about tag: {tag_data.name}")
            .add_field("Created by", f"{self.bot.get_user(tag_data.owner_id)}", inline=False)
            .add_field("Tag ID", tag_data.id, inline=False)
            .add_field("Created on:", disnake.utils.format_dt(tag_data.created_at, "R"))
        )
