import json
import logging
from typing import Dict, Any, Tuple
from app.core.database import get_db
from app.services.rockstar_api import fetch_newswire_posts
from app.services.article_parser import fetch_article_details

logger = logging.getLogger(__name__)


async def sync_all_news() -> Tuple[int, int]:
    """
    Syncs news across GTA 6, GTA Online, and General Rockstar Newswire.
    Returns (new_count, updated_count).
    """
    logger.info("Starting Rockstar news synchronization...")

    # Fetch from all three streams
    gta6_posts = await fetch_newswire_posts(tag_id_hash="vi", limit=15)
    online_posts = await fetch_newswire_posts(tag_id_hash="gta-online", limit=15)
    general_posts = await fetch_newswire_posts(tag_id_hash=None, limit=15)

    # Deduplicate in-memory by id
    all_posts: Dict[str, Dict[str, Any]] = {}
    for post in gta6_posts + online_posts + general_posts:
        pid = post["id"]
        if pid not in all_posts:
            all_posts[pid] = post

    new_count = 0
    updated_count = 0

    async with get_db() as conn:
        for post in all_posts.values():
            pid = post["id"]

            cursor = await conn.execute("SELECT id, summary FROM articles WHERE id = ?", (pid,))
            existing = await cursor.fetchone()

            summary = None
            weekly_details = None

            if not existing:
                try:
                    details = await fetch_article_details(post["url"])
                    summary = details.get("summary")
                    weekly_details = details
                except Exception as e:
                    logger.warning(f"Could not fetch details for {post['url']}: {e}")

                tags_json = json.dumps(post["tags"])
                await conn.execute("""
                    INSERT INTO articles (
                        id, title, slug, url, image_url, summary, category, tags, published_at, is_weekly_event, notified
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                """, (
                    pid,
                    post["title"],
                    post["slug"],
                    post["url"],
                    post["image_url"],
                    summary,
                    post["category"],
                    tags_json,
                    post["published_at"],
                    1 if post["is_weekly_event"] else 0
                ))
                new_count += 1

                if post["is_weekly_event"] and weekly_details:
                    bonuses_json = json.dumps(weekly_details.get("bonuses", []))
                    discounts_json = json.dumps(weekly_details.get("discounts", []))
                    await conn.execute("""
                        INSERT OR REPLACE INTO weekly_events (
                            article_id, title, url, summary, bonuses, discounts, podium_vehicle, prize_ride
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        pid,
                        post["title"],
                        post["url"],
                        summary,
                        bonuses_json,
                        discounts_json,
                        weekly_details.get("podium_vehicle"),
                        weekly_details.get("prize_ride")
                    ))
            else:
                tags_json = json.dumps(post["tags"])
                await conn.execute("""
                    UPDATE articles
                    SET title = ?, slug = ?, url = ?, image_url = ?, category = ?, tags = ?, published_at = ?, is_weekly_event = ?
                    WHERE id = ?
                """, (
                    post["title"],
                    post["slug"],
                    post["url"],
                    post["image_url"],
                    post["category"],
                    tags_json,
                    post["published_at"],
                    1 if post["is_weekly_event"] else 0,
                    pid
                ))
                updated_count += 1

        await conn.commit()
        logger.info(f"Sync complete. New: {new_count}, Updated: {updated_count}")
        return new_count, updated_count
