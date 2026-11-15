from fastapi import APIRouter
from datetime import datetime, timezone
from app.services.synchronizer import sync_all_news
from app.models.schemas import SyncResult
from app.core.database import get_db

router = APIRouter(prefix="/sync", tags=["Synchronization"])


@router.post("", response_model=SyncResult)
async def trigger_manual_sync():
    """Manually triggers an immediate pull and sync from official Rockstar feeds."""
    new_count, updated_count = await sync_all_news()
    return SyncResult(
        new_articles_count=new_count,
        updated_articles_count=updated_count,
        message=f"Sync successful. Ingested {new_count} new articles, updated {updated_count}.",
        synced_at=datetime.now(timezone.utc).isoformat()
    )


@router.get("/status")
async def get_sync_status():
    """Returns database metrics and synchronization health."""
    async with get_db() as conn:
        total_cursor = await conn.execute("SELECT COUNT(*) FROM articles")
        total_articles = (await total_cursor.fetchone())[0]

        gta6_cursor = await conn.execute("SELECT COUNT(*) FROM articles WHERE category = 'gta6'")
        gta6_count = (await gta6_cursor.fetchone())[0]

        online_cursor = await conn.execute("SELECT COUNT(*) FROM articles WHERE category = 'gta_online'")
        online_count = (await online_cursor.fetchone())[0]

        weekly_cursor = await conn.execute("SELECT COUNT(*) FROM weekly_events")
        weekly_count = (await weekly_cursor.fetchone())[0]

        latest_cursor = await conn.execute("SELECT published_at FROM articles ORDER BY published_at DESC LIMIT 1")
        latest_row = await latest_cursor.fetchone()
        latest_article_date = latest_row[0] if latest_row else None

        return {
            "status": "healthy",
            "total_articles": total_articles,
            "gta6_articles": gta6_count,
            "gta_online_articles": online_count,
            "weekly_events_tracked": weekly_count,
            "latest_article_published_at": latest_article_date,
            "checked_at": datetime.now(timezone.utc).isoformat()
        }
