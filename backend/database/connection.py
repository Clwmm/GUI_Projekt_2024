from asyncpg import create_pool
from typing import AsyncGenerator

DATABASE_URL = "postgresql://user:password@localhost:5432/yourdb"

async def get_db() -> AsyncGenerator:
    pool = await create_pool(DATABASE_URL)
    async with pool.acquire() as connection:
        yield connection
