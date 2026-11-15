# AI Agent Roadmap & Tasks

This task backlog provides concrete next steps for future AI development sessions on this codebase.

---

## 🎯 P0: Core Stability & Downstream Integration

- [x] Reverse-engineer official Rockstar Games GraphQL endpoint (`graph.rockstargames.com`).
- [x] Implement async SQLite persistence layer and background scheduler.
- [x] Implement paginated `/news`, `/news/gta6`, `/news/online`, and `/weekly/current` endpoints.
- [x] Containerize application with `Dockerfile` and `docker-compose.yml`.
- [x] Write pytest test suite (100% passing).
- [ ] **Webhook Dispatcher**:
  - Add a table `webhook_subscriptions` (`id`, `url`, `secret`, `categories`).
  - Whenever `sync_all_news()` detects new articles (`notified = 0`), dispatch an HTTP POST payload to subscribed endpoints (e.g. your Telegram bot backend or Discord webhook).
  - Update `articles.notified = 1` once dispatched.

---

## 🚀 P1: Syndication & Advanced Sources

- [ ] **RSS / Atom XML Feed Generator**:
  - Add `/api/v1/feed.xml` and `/api/v1/feed/gta6.xml` endpoints returning valid RSS 2.0 / Atom feeds.
  - Allows direct subscription in feed readers (Feedly, Inoreader, Newsboat).
- [ ] **Rockstar Support Status Scraper**:
  - Add scheduled check of Rockstar game server health status.
  - Expose `/api/v1/status/servers` (GTA Online PC, PS5, Xbox Series X/S status).
- [ ] **Rockstar YouTube Channel Video Integration**:
  - Fallback / supplement video trailers directly into the database.

---

## ⚡ P2: Scaling & Caching

- [ ] **Redis Cache Layer**:
  - Add optional Redis cache for hot endpoints (`/news/gta6`, `/weekly/current`) with TTL invalidation on new article ingestion.
- [ ] **PostgreSQL Support**:
  - Support PostgreSQL via `asyncpg` / `SQLAlchemy` when switching `DATABASE_URL` in `.env`.

