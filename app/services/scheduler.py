import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.config import settings
from app.services.synchronizer import sync_all_news

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def scheduled_sync():
    try:
        logger.info("Executing scheduled news sync...")
        await sync_all_news()
    except Exception as e:
        logger.error(f"Scheduled sync encountered an error: {e}", exc_info=True)


def start_scheduler():
    interval = max(1, settings.POLL_INTERVAL_MINUTES)
    scheduler.add_job(
        scheduled_sync,
        "interval",
        minutes=interval,
        id="rockstar_news_sync",
        replace_existing=True
    )
    scheduler.start()
    logger.info(f"Background scheduler started (interval: every {interval} minutes).")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Background scheduler shut down.")

