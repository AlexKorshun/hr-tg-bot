import asyncpg, datetime
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


async def get_pass_role_by_email(email: str) -> Role | None:
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT role
                FROM passwords
                WHERE email = %s
                """,
                (email,),
            )
            row = await cur.fetchone()
            return Role(row[0]) if row else None

        
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
async def get_users_count() -> int:
    await init_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT COUNT(*) FROM users")
            count = await cur.fetchone()
            return count[0] if count else 0

async def update_user_last_use(telegram_id: TelegramID) -> None:
    await init_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                UPDATE users
                   SET last_use = CURRENT_TIMESTAMP
                 WHERE telegram_id = %s
                """,
                (telegram_id,),
            )

async def get_active_users_count() -> int:
    await init_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT count(*)
                FROM users
                WHERE last_use >= CURRENT_TIMESTAMP - INTERVAL '7 day'
                """
            )
            count = await cur.fetchone()
            return count[0] if count else 0
        

async def get_excursions_count() -> int:
    await init_pool()  # Инициализация пула соединений (если требуется)
    
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT COUNT(*) FROM excursions;"
            )
            count = await cur.fetchone()
            return count[0] if count else 0
        
async def get_excursion_by_index(index: int) -> tuple[str, str, str] | None:
    await init_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT id ,date, description 
                FROM excursions
                ORDER BY id  -- или другой подходящий столбец для сортировки
                OFFSET %s
                LIMIT 1;
                """,
                (index,)  # Параметр для OFFSET
            )
            result = await cur.fetchone()
            return result if result else None

import datetime

async def register_excursion(excursion_id: int, user_telegram_id: int) -> int:
    await init_pool()
    
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            current_time = datetime.datetime.now()
            
            await cur.execute(
                "INSERT INTO excursion_registrations (excursion_id, user_telegram_id, created_at) "
                "VALUES (%s, %s, %s) "
                "ON CONFLICT (excursion_id, user_telegram_id) DO NOTHING RETURNING id",
                (excursion_id, user_telegram_id, current_time)
            )
            
            result = await cur.fetchone()
            return result[0] if result else None
