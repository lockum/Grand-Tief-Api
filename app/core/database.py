import aiosqlite
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from app.core.config import settings

DB_FILE = settings.DATABASE_PATH


async def get_db_connection() -> aiosqlite.Connection:
    """Returns an open aiosqlite Connection object."""
    conn = await aiosqlite.connect(DB_FILE)
    conn.row_factory = aiosqlite.Row
    return conn


@asynccontextmanager
async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Async context manager for acquiring and safely closing a database connection."""
    conn = await get_db_connection()
    try:
        yield conn
    finally:
        await conn.close()


async def init_db():
    async with get_db() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                slug TEXT,
                url TEXT NOT NULL,
                image_url TEXT,
                summary TEXT,
                category TEXT NOT NULL,
                tags TEXT,
                published_at TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_weekly_event INTEGER DEFAULT 0,
                notified INTEGER DEFAULT 0
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS weekly_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id TEXT UNIQUE,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                summary TEXT,
                bonuses TEXT,
                discounts TEXT,
                podium_vehicle TEXT,
                prize_ride TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (article_id) REFERENCES articles(id)
            )
        """)

        # Indexes for fast querying
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_at DESC)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_articles_notified ON articles(notified)")
        await conn.commit()
