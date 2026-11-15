# AI Agent Architecture Guide

This document is intended for AI agents (and human developers) onboarding to or extending the **ViceWire** codebase.

---

## 1. What This Service Is (And Is Not)

- **IS**: A dedicated, headless backend API service that scrapes, aggregates, enriches, stores, and serves official Rockstar Games news, GTA VI updates, and GTA Online weekly events.
- **IS NOT**: A Telegram bot or consumer UI. The Telegram bot is built as an independent service in a separate repository that consumes this API over HTTP.

---

## 2. Upstream Rockstar Integration Mechanics

### Endpoint
```
POST https://graph.rockstargames.com/
```

### Essential Headers
```python
{
    "User-Agent": "Mozilla/5.0 ...",
    "Content-Type": "application/json",
    "Origin": "https://www.rockstargames.com",
    "Referer": "https://www.rockstargames.com/newswire"
}
```
*Note: Without `Origin` and `Referer`, some edge CDNs may reject GraphQL POST requests.*

### Query & Variables
We execute `query NewswireList($locale: String!, $page: Int!, $limit: Int, $tagIdHash: String, $metaUrl: String!)`.
- When filtering for **GTA VI**: pass `tagIdHash: "vi"`.
- When filtering for **GTA Online**: pass `tagIdHash: "gta-online"`.
- When fetching all newswire: omit `tagIdHash` or pass `None`.

### Data Extraction
From the GraphQL response `data.posts.results`:
- `id`: Unique hash string (e.g. `89834o94713o21`). Use this as `articles.id` primary key.
- `title`: HTML string. Always pass through `clean_html()` (`BeautifulSoup(raw, "html.parser").get_text()`) to strip tags.
- `preview_images_parsed.newswire_block`: Contains `d16x9`, `square`, and `_fallback`. Use `d16x9` first.

---

## 3. Database Architecture (`app/core/database.py`)

- **Engine**: SQLite via `aiosqlite`.
- **Concurrency Pattern**: Always use the async context manager:
  ```python
  async with get_db() as conn:
      cursor = await conn.execute("SELECT ...")
      ...
  ```
  *Never call `aiosqlite.connect()` manually without closing or doubly-awaiting it.*
- **Schema**:
  - `articles`: Primary store of deduplicated articles.
  - `weekly_events`: Enriched weekly bonus records (bonuses, discounts, vehicle podium/prize ride).

---

## 4. Ingestion & Synchronization Flow

```
1. app/services/scheduler.py (Every 15m)
        │
        ▼
2. app/services/synchronizer.py: sync_all_news()
        │
        ├─► fetch_newswire_posts(tag_id_hash="vi")
        ├─► fetch_newswire_posts(tag_id_hash="gta-online")
        └─► fetch_newswire_posts(tag_id_hash=None)
        │
        ▼
3. Deduplicate in-memory by article `id`
        │
        ▼
4. Check DB for existence:
   - If NEW:
       ├─► Call fetch_article_details(url) for OG description & bonus parsing
       ├─► INSERT INTO articles (notified = 0)
       └─► IF is_weekly_event: INSERT INTO weekly_events
   - If EXISTING:
       └─► UPDATE metadata if altered
```

---

## 5. Adding New Routes or Features

1. Create/update schema in `app/models/schemas.py`.
2. Add route handlers in `app/api/routes/<domain>.py`.
3. Mount router in `app/main.py`.
4. Add unit/integration test in `tests/test_api.py`.
5. Run tests:
   ```bash
   ./.venv/bin/pytest tests/
   ```

