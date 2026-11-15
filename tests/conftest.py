import pytest
import pytest_asyncio
import os
import httpx
from app.core.config import settings
from app.core.database import init_db, get_db
from app.main import app

settings.DATABASE_PATH = "./test_gta_news.db"


@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    await init_db()
    async with get_db() as conn:
        await conn.execute("""
            INSERT OR REPLACE INTO articles (
                id, title, slug, url, image_url, summary, category, tags, published_at, is_weekly_event, notified
            ) VALUES 
            ('test-gta6-1', 'GTA VI Trailer Released', 'gta-vi-trailer', 'https://rockstargames.com/VI', 'https://img.jpg', 'GTA 6 in Vice City', 'gta6', '["GTA6"]', '2026-11-10T12:00:00Z', 0, 0),
            ('test-online-1', 'GTA Online Weekly Event: Double Cash', 'weekly-double-cash', 'https://rockstargames.com/online', 'https://img2.jpg', 'Double cash on heists', 'gta_online', '["GTA Online"]', '2026-11-12T12:00:00Z', 1, 0)
        """)
        await conn.execute("""
            INSERT OR REPLACE INTO weekly_events (
                id, article_id, title, url, summary, bonuses, discounts, podium_vehicle, prize_ride
            ) VALUES (
                1, 'test-online-1', 'GTA Online Weekly Event: Double Cash', 'https://rockstargames.com/online', 'Double cash on heists', '["2x Cash on Heists"]', '["40% off Supercars"]', 'Pegassi Zentorno', 'Annis Elegy RH8'
            )
        """)
        await conn.commit()

    yield

    if os.path.exists("./test_gta_news.db"):
        try:
            os.remove("./test_gta_news.db")
        except OSError:
            pass


@pytest_asyncio.fixture
async def async_client():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        yield client
