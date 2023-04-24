from __future__ import annotations

import datetime

import asyncpg  # type: ignore
import attrs

__all__: tuple[str] = ("DatabaseHandler",)


@attrs.define
class DatabaseHandler:
    pool: asyncpg.Pool

    async def setup(self) -> None:
        """Execute migrations and CREATE TABLE queries here."""
        await self.pool.execute(  # type: ignore
            """
            CREATE TABLE IF NOT EXISTS devconnect_tags (
                id INTEGER, 
                name VARCHAR,
                owner_id BIGINT,
                content VARCHAR,
                created_at TIMESTAMP
            )
            """
        )

    async def add_tag(self, name: str, owner: int, content: str) -> None:
        last_id: int = await self.pool.fetchval("SELECT MAX(id) FROM devconnect_tags")  # type: ignore
        await self.pool.execute(  # type: ignore
            """
            INSERT INTO devconnect_tags
            VALUES ($1, $2, $3, $4, $5)
            """,
            (last_id or 0) + 1,
            name.lower(),
            owner,
            content[:4000],
            datetime.datetime.now(),
        )
