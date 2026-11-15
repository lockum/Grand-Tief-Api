# AI Agent Architecture Guide

This document is intended for AI agents (and human developers) onboarding to or extending the **ViceWire** codebase.

---

## 1. What This Service Is (And Is Not)

- **IS**: A dedicated, headless backend API service that scrapes, aggregates, enriches, stores, and serves official Rockstar Games news, GTA VI updates, and GTA Online weekly events.
- **IS NOT**: A Telegram bot or consumer UI. The Telegram bot is built as an independent service in a separate repository that consumes this API over HTTP with the `reader` user credentials.

---

## 2. Authentication & Authorization

All data endpoints are secured using **HTTP Basic Authentication** in `app/core/security.py`:
- **Read-Only User** (`settings.API_READONLY_USERNAME`, `settings.API_READONLY_PASSWORD`):
  - Used by external consumers (Telegram bots, mobile apps).
  - Can access `/api/v1/news*`, `/api/v1/weekly*`, and `/api/v1/sync/status`.
  - Dependent function: `require_readonly_user`.
- **Admin User** (`settings.API_ADMIN_USERNAME`, `settings.API_ADMIN_PASSWORD`):
  - Full access, including triggering manual synchronization (`POST /api/v1/sync`).
  - Dependent function: `require_admin_user`.
- **Public Endpoints**: `/` and `/health` stay public for uptime monitors and container orchestrators.

---

## 3. Upstream Rockstar Integration Mechanics

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

### Query & Variables
We execute `query NewswireList($locale: String!, $page: Int!, $limit: Int, $tagIdHash: String, $metaUrl: String!)`.
- When filtering for **GTA VI**: pass `tagIdHash: "vi"`.
- When filtering for **GTA Online**: pass `tagIdHash: "gta-online"`.
- When fetching all newswire: omit `tagIdHash` or pass `None`.

---

## 4. Database Architecture (`app/core/database.py`)

- **Engine**: SQLite via `aiosqlite`.
- **Concurrency Pattern**: Always use the async context manager:
  ```python
  async with get_db() as conn:
      cursor = await conn.execute("SELECT ...")
      ...
  ```
- **Schema**:
  - `articles`: Primary store of deduplicated articles.
  - `weekly_events`: Enriched weekly bonus records (bonuses, discounts, vehicle podium/prize ride).

---

## 5. Testing Requirements
- Run the test suite:
  ```bash
  ./.venv/bin/pytest tests/
  ```
- All new endpoints must have corresponding authenticated and unauthorized test cases in `tests/test_api.py`.
