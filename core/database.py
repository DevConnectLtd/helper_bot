from __future__ import annotations

import asyncpg  # type: ignore
import attrs

__all__: tuple[str] = ("DatabaseHandler",)


@attrs.define
class DatabaseHandler:
    pool: asyncpg.Pool

    async def setup(self) -> None:
        """Execute migrations and CREATE TABLE queries here."""
