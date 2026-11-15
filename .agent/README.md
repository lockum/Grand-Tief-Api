# AI Agent Workspace Guide

Welcome! This directory contains essential context, architectural patterns, coding conventions, and a prioritized task backlog for any AI agent interacting with the **ViceWire** codebase.

---

## 🧭 Orientation & Fast Context

- **Repository Role**: Headless news and updates aggregation REST API for Grand Theft Auto VI and GTA Online.
- **Tech Stack**: Python 3.10+, FastAPI, `aiosqlite` (async SQLite), `httpx`, `apscheduler`, `pydantic v2`, `pytest`.
- **Primary Data Upstream**: Rockstar Games GraphQL Gateway at `https://graph.rockstargames.com/` (sub-second official structured news).
- **Authentication**: HTTP Basic Auth with two roles:
  - `reader` (Read-only for downstream consumers like Telegram/Discord bots).
  - `admin` (Full access, including manual sync triggers).
- **Consumer Decoupling**: Downstream consumers (like Telegram Bots) are NOT housed in this repository; they communicate with this service over HTTP.

---

## 📂 Navigation Index

| Document | Purpose |
| :--- | :--- |
| **[`instructions.md`](./instructions.md)** | Mandatory operational rules, command execution standards, and pre-commit checks. |
| **[`ARCHITECTURE_GUIDE.md`](./ARCHITECTURE_GUIDE.md)** | Technical breakdown of upstream GraphQL queries, database schemas, and background ingestion loops. |
| **[`CONVENTIONS.md`](./CONVENTIONS.md)** | Code standards, typing expectations, async patterns, and error handling conventions. |
| **[`TASKS.md`](./TASKS.md)** | Prioritized roadmap of upcoming features (Webhooks, RSS feeds, Redis caching). |

---

## ⚡ Quick Rules of Thumb

1. **Always run tests after making changes**:
   ```bash
   pytest tests/
   ```
2. **Never break async SQLite connection pooling**:
   Always use `async with get_db() as conn:`. Never invoke `aiosqlite.connect()` manually without proper closing.
3. **Respect user roles**:
   Read endpoints must be protected with `require_readonly_user`. Mutating/trigger endpoints must use `require_admin_user`. Public endpoints are strictly `/` and `/health`.
