import asyncpg
from typing import Optional
from app.core.config import settings

class Database:
    pool: Optional[asyncpg.Pool] = None

db = Database()

async def connect_to_db():
    db.pool = await asyncpg.create_pool(
        dsn=settings.DATABASE_URL,
        min_size=2,
        max_size=10
    )
    print("PostgreSQL connection pool established.")

async def close_db_connection():
    if db.pool:
        await db.pool.close()
        print("PostgreSQL connection pool closed.")