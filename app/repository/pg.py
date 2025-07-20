import asyncpg
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
from typing import Optional, List

from app.config import DATABASE_URL
from app.models.user import User, UserID, TelegramID, Role
from app.repository.mapper import map_user_row

pool: AsyncConnectionPool | None = None

async def init_pool() -> AsyncConnectionPool:
    global pool
    if pool is None:
        pool = AsyncConnectionPool(conninfo=DATABASE_URL, open=False)
        await pool.open()
        await pool.wait()
    return pool


async def get_user_by_id(telegram_id: TelegramID) -> Optional[User]:
    await init_pool()
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT * FROM users WHERE telegram_id = %s",
                (telegram_id,),
            )
            row = await cur.fetchone()
    return map_user_row(row) if row else None

async def create_user(telegram_id: TelegramID, username: str, full_name: str, role: Role, email: str) -> None:
    await init_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO users (
                    telegram_id, username, full_name, email, role
                )
                VALUES (
                    %s, %s, %s, %s, %s
                )
                ON CONFLICT (telegram_id) DO NOTHING
                """,
                (telegram_id, username, full_name, email, role.value),
            )


async def get_pass_hash_by_email(email: str) -> dict | None:
    await init_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT password_hash, used
                FROM passwords
                WHERE email = %s
                  AND used = FALSE
                """,
                (email,),
            )
            row = await cur.fetchone()
            return row if row else None 


async def create_hash(email: str, hash: str) -> None:
    await init_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO passwords (email, password_hash, used)
                VALUES (%s, %s, FALSE)
                ON CONFLICT (email) DO UPDATE
                  SET password_hash = EXCLUDED.password_hash,
                      used = FALSE
                """,
                (email, hash),
            )

async def set_password_used(email: str) -> None:
    await init_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                UPDATE passwords
                   SET used = TRUE
                 WHERE email = %s
                """,
                (email,),
            )