from __future__ import annotations

import typing

import asyncpg  # type: ignore
import disnake
from disnake.ext import commands

from core.database import DatabaseHandler
from core.logger import create_logging_setup
from core.utils import MISSING, EnvironmentVariables, Missing, MissingOr, load_and_verify_envs

__all__: tuple[str] = ("HelperBot",)


class HelperBot(commands.Bot):
    _pool: MissingOr[asyncpg.Pool] = MISSING
    _db: MissingOr[DatabaseHandler] = MISSING
    envs: EnvironmentVariables = load_and_verify_envs()
    logger = create_logging_setup()

    def __init__(self) -> None:
        super().__init__(
            command_prefix="!",
            strip_after_prefix=True,
            case_insensitive=True,
            intents=disnake.Intents(
                guild_messages=True,
                message_content=True,
                members=True,
                presences=True,
                emojis=True,
                guild_reactions=True,
            ),
            allowed_mentions=disnake.AllowedMentions(everyone=False, replied_user=False),
        )
        self.load_extension("jishaku")

    @property
    def pool(self) -> asyncpg.Pool:
        assert not isinstance(self._pool, Missing)
        return self._pool

    @property
    def db(self) -> DatabaseHandler:
        assert not isinstance(self._db, Missing)
        return self._db

    async def setups(self) -> None:
        self._pool = await asyncpg.create_pool(self.envs.PGSQL_URL)  # type: ignore
        self._db = DatabaseHandler(self.pool)
        await self.db.setup()

    async def start(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        await self.setups()
        await super().start(*args, **kwargs)
