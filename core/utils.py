from __future__ import annotations

import importlib
import inspect
import logging
import os
import pathlib
import sys
import typing

import asyncpg  # type: ignore
import attrs
import disnake
import dotenv
from disnake.ext import commands

from core.database import DatabaseHandler

if typing.TYPE_CHECKING:
    from core.bot import HelperBot

__all__: tuple[str, ...] = ("EnvironmentVariables", "load_and_verify_envs", "parse_cogs", "BotBase", "HelperCog")


class Missing:
    ...


MISSING = Missing()

T = typing.TypeVar("T")

MissingOr = typing.Union[Missing, T]
ColorLike = typing.Union[int, disnake.Color]


@attrs.define(kw_only=True)
class EnvironmentVariables:
    BOT_TOKEN: str
    PGSQL_URL: str


class HelperCog(commands.Cog):
    """No description provided."""

    bot: HelperBot
    hidden: bool = False

    def __init__(self, bot: HelperBot) -> None:
        self.bot = bot


class BotBase(commands.Bot):
    envs: EnvironmentVariables
    cogs: dict[str, HelperCog]
    _pool: MissingOr[asyncpg.Pool] = MISSING
    _db: MissingOr[DatabaseHandler] = MISSING

    @property
    def pool(self) -> asyncpg.Pool:
        assert not isinstance(self._pool, Missing)
        return self._pool

    @property
    def db(self) -> DatabaseHandler:
        assert not isinstance(self._db, Missing)
        return self._db

    async def start(self) -> None:
        await self.setups()
        await super().start(self.envs.BOT_TOKEN)

    async def setups(self) -> None:
        self._pool = await asyncpg.create_pool(self.envs.PGSQL_URL)  # type: ignore
        self._db = DatabaseHandler(self.pool)
        await self.db.setup()


def parse_cogs(path: str | pathlib.Path) -> dict[str, type[HelperCog]]:
    path_str = path.as_posix().replace("/", ".")[:-3] if isinstance(path, pathlib.Path) else path
    module = importlib.import_module(path_str)
    cogs: list[tuple[str, HelperCog]] = inspect.getmembers(
        module, lambda item: inspect.isclass(item) and HelperCog in item.mro()
    )
    return dict(cogs)


dotenv.load_dotenv()


def load_and_verify_envs() -> EnvironmentVariables:
    required: set[str] = set([a.name for a in EnvironmentVariables.__attrs_attrs__])  # type: ignore
    if not ((validated := (required)).intersection(os.environ)) == required:
        logging.error(
            "\n".join(
                (
                    "ENV ERROR!",
                    "Missing required environmental variables.",
                    "-----------------------------------------",
                    "Missing:",
                    "--------",
                    "%s",
                )
            ),
            required.difference(validated),
        )
        print(
            validated,
            required,
        )
        sys.exit()
    else:
        return EnvironmentVariables(**{k: v for k, v in os.environ.items() if k in required})
