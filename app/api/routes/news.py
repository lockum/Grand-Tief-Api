from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
import json
from app.core.database import get_db
from app.core.security import require_readonly_user
from app.models.schemas import ArticleResponse, PaginatedArticlesResponse

router = APIRouter(
    prefix="/news",
    tags=["News"],
    dependencies=[Depends(require_readonly_user)]
)


def row_to_article(row) -> ArticleResponse:
    tags = []
    if row["tags"]:
        try:
            tags = json.loads(row["tags"])
        except Exception:
            tags = []

    return ArticleResponse(
        id=row["id"],
        title=row["title"],
        slug=row["slug"],
        url=row["url"],
        image_url=row["image_url"],
        summary=row["summary"],
        category=row["category"],
        tags=tags,
        published_at=row["published_at"],
        created_at=row["created_at"],
        is_weekly_event=bool(row["is_weekly_event"]),
        notified=bool(row["notified"])
    )


@router.get("", response_model=PaginatedArticlesResponse)
async def get_all_news(
    category: Optional[str] = Query(None, description="Filter by category: 'gta6', 'gta_online', 'rockstar'"),
    search: Optional[str] = Query(None, description="Search keyword in title or summary"),
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=10, ge=1, le=50, description="Items per page")
):
    offset = (page - 1) * limit
    async with get_db() as conn:
        where_clauses = []
        params = []

        if category:
            where_clauses.append("category = ?")
            params.append(category)

        if search:
            where_clauses.append("(title LIKE ? OR summary LIKE ?)")
            search_param = f"%{search}%"
            params.extend([search_param, search_param])

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        count_cursor = await conn.execute(f"SELECT COUNT(*) FROM articles {where_sql}", params)
        total = (await count_cursor.fetchone())[0]

        query = f"""
            SELECT * FROM articles
            {where_sql}
            ORDER BY published_at DESC, created_at DESC
            LIMIT ? OFFSET ?
        """
        cursor = await conn.execute(query, params + [limit, offset])
        rows = await cursor.fetchall()

        results = [row_to_article(r) for r in rows]
        return PaginatedArticlesResponse(
            total=total,
            page=page,
            limit=limit,
            results=results
        )


@router.get("/gta6", response_model=PaginatedArticlesResponse)
async def get_gta6_news(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=50)
):
    """Shortcut endpoint for all GTA 6 updates & news."""
    return await get_all_news(category="gta6", search=None, page=page, limit=limit)


@router.get("/online", response_model=PaginatedArticlesResponse)
async def get_online_news(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=50)
):
    """Shortcut endpoint for GTA Online updates & news."""
    return await get_all_news(category="gta_online", search=None, page=page, limit=limit)


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article_by_id(article_id: str):
    async with get_db() as conn:
        cursor = await conn.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Article not found")
        return row_to_article(row)
