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
        await self.pool.execute(  # type: ignore
            """
            CREATE TABLE IF NOT EXISTS devconnect_warns (
                id INTEGER, 
                mod_id BIGINT, 
                user_id BIGINT, 
                reason VARCHAR, 
                created_at TIMESTAMP
            )
            """
        )
        await self.pool.execute(  # type: ignore
            """
            CREATE TABLE IF NOT EXISTS devconnect_reps (
                user_id BIGINT,
                reps INTEGER DEFAULT 0
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

    async def add_warn(self, mod_id: int, user_id: int, reason: str) -> int:
        last_id: int = await self.pool.fetchval("SELECT MAX(id) FROM devconnect_warns")  # type: ignore
        await self.pool.execute(  # type: ignore
            """
            INSERT INTO devconnect_warns
            VALUES ($1, $2, $3, $4, $5)
            """,
            (warns := ((last_id or 0) + 1)),  # type: ignore
            mod_id,
            user_id,
            reason,
            datetime.datetime.now(),
        )
        assert isinstance(warns, int)
        return warns

    async def add_rep(self, user_id: int, reps: int = 1) -> int:
        check_existence: int | None = await self.pool.fetchval(  # type: ignore
            "SELECT reps FROM devconnect_reps WHERE user_id = $1", user_id
        )
        if check_existence is None:
            await self.pool.execute(  # type: ignore
                "INSERT INTO devconnect_reps VALUES ($1, $2)",
                user_id,
                reps,
            )
            return reps
        await self.pool.execute(  # type: ignore
            "UPDATE devconnect_reps SET reps = reps + $1 WHERE user_id = $2",
            reps,
            user_id,
        )
        assert isinstance(check_existence, int)
        return check_existence + reps

    async def remove_rep(self, user_id: int, reps: int) -> int:
        current_reps: int | None = await self.pool.fetchval(  # type: ignore
            "SELECT reps FROM devconnect_reps WHERE user_id = $1",
            user_id,
        )
        if current_reps is None:
            await self.add_rep(user_id, 0)
        assert isinstance(current_reps, int)
        new_reps = (current_reps - reps) if (current_reps - reps) >= 0 else 0
        await self.pool.execute(  # type: ignore
            "UPDATE devconnect_reps SET reps = $1 WHERE user_id = $2",
            new_reps,
            user_id,
        )
        return new_reps
