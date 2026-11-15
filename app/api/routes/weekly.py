from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
import json
from app.core.database import get_db
from app.core.security import require_readonly_user
from app.models.schemas import WeeklyEventResponse

router = APIRouter(
    prefix="/weekly",
    tags=["GTA Online Weekly Events"],
    dependencies=[Depends(require_readonly_user)]
)


def row_to_weekly(row) -> WeeklyEventResponse:
    bonuses = []
    discounts = []
    if row["bonuses"]:
        try:
            bonuses = json.loads(row["bonuses"])
        except Exception:
            bonuses = []
    if row["discounts"]:
        try:
            discounts = json.loads(row["discounts"])
        except Exception:
            discounts = []

    return WeeklyEventResponse(
        id=row["id"],
        article_id=row["article_id"],
        title=row["title"],
        url=row["url"],
        summary=row["summary"],
        bonuses=bonuses,
        discounts=discounts,
        podium_vehicle=row["podium_vehicle"],
        prize_ride=row["prize_ride"],
        created_at=row["created_at"]
    )


@router.get("/current", response_model=WeeklyEventResponse)
async def get_current_weekly_event():
    """Returns the most recent GTA Online weekly event with bonuses and discounts."""
    async with get_db() as conn:
        cursor = await conn.execute("""
            SELECT * FROM weekly_events
            ORDER BY created_at DESC
            LIMIT 1
        """)
        row = await cursor.fetchone()
        if not row:
            art_cursor = await conn.execute("""
                SELECT * FROM articles
                WHERE is_weekly_event = 1
                ORDER BY published_at DESC, created_at DESC
                LIMIT 1
            """)
            art_row = await art_cursor.fetchone()
            if not art_row:
                raise HTTPException(status_code=404, detail="No weekly events found yet. Trigger a sync first.")
            return WeeklyEventResponse(
                id=1,
                article_id=art_row["id"],
                title=art_row["title"],
                url=art_row["url"],
                summary=art_row["summary"],
                bonuses=[],
                discounts=[],
                podium_vehicle=None,
                prize_ride=None,
                created_at=art_row["created_at"]
            )

        return row_to_weekly(row)


@router.get("/history", response_model=List[WeeklyEventResponse])
async def get_weekly_event_history(limit: int = Query(default=10, ge=1, le=50)):
    """Returns past GTA Online weekly updates."""
    async with get_db() as conn:
        cursor = await conn.execute("""
            SELECT * FROM weekly_events
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        rows = await cursor.fetchall()
        return [row_to_weekly(r) for r in rows]
