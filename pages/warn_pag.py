from __future__ import annotations

import typing

import disnake
from disnake.ext import commands

from core.bot import HelperBot

if typing.TYPE_CHECKING:
    from core.models import WarnData


class WarnPaginator(disnake.ui.View):
    children: list[disnake.ui.Button[HelperBot]]  # type: ignore
    ctx: commands.Context[HelperBot]
    warns: list[WarnData]
    last_inter: disnake.MessageInteraction
    message: disnake.Message
    index: int

    def __init__(
        self, ctx: commands.Context[HelperBot], warns: typing.Iterable[WarnData], *, timeout: float | None = 180
    ) -> None:
        self.ctx = ctx
        self.warns = list(warns)
        self.index = 0

        super().__init__(timeout=timeout)

    def prepare_embed(self) -> disnake.Embed:
        warn_data = self.warns[self.index]
        return (
            self.ctx.bot.generic_embed(self.ctx, warn_data.reason)
            .add_field("Target", f"{self.ctx.bot.get_user(warn_data.user_id)} ({warn_data.user_id})", inline=False)
            .add_field("Moderator", f"{self.ctx.bot.get_user(warn_data.mod_id)} ({warn_data.mod_id})", inline=False)
            .add_field("Created on:", disnake.utils.format_dt(warn_data.created_at, "R"), inline=False)
            .set_author(name=f"Warn #{warn_data.id}")
            .set_footer(text=f"Showing warns for {warn_data.user_id}")
        )

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if interaction.user.id == self.ctx.author.id:
            self.last_inter = interaction
            return True
        await interaction.send("This paginator does not belong to you.", ephemeral=True)
        return False

    async def update_msg(self) -> None:
        if self.index == 0:
            self.prev.disabled = True
        elif self.index == len(self.warns):
            self.next.disabled = True
        await self.last_inter.response.edit_message(embed=self.prepare_embed())

    async def on_timeout(self) -> None:
        for button in self.children:
            button.disabled = True
        await self.message.edit(view=self)

    @disnake.ui.button(emoji="⬅️", style=disnake.ButtonStyle.blurple)
    async def prev(self, button: disnake.ui.Button[WarnPaginator], inter: disnake.MessageInteraction) -> None:
        self.index -= 1
        await self.update_msg()

    @disnake.ui.button(emoji="➡️", style=disnake.ButtonStyle.blurple)
    async def next(self, button: disnake.ui.Button[WarnPaginator], inter: disnake.MessageInteraction) -> None:
        self.index += 1
        await self.update_msg()

    @disnake.ui.button(emoji="❎", style=disnake.ButtonStyle.danger)
    async def stawp(self, _: ..., inter: disnake.MessageInteraction) -> None:
        await inter.response.defer()
        await self.on_timeout()
