# ViceWire API

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A high-performance, asynchronous REST API service that ingests, enriches, and serves official **Grand Theft Auto VI** news, **GTA Online** weekly events, vehicle rewards, and Rockstar Games announcements directly from official sources.

Designed as an independent backend engine that can be consumed by Telegram bots, Discord bots, web dashboards, or mobile widgets.

---

## ⚡ Highlights

- **Direct Official Ingestion**: Pulls structured data directly from Rockstar Games' internal GraphQL gateway (`https://graph.rockstargames.com/`), delivering sub-second updates without fragile HTML parsing.
- **Categorization**: Auto-filters by `gta6` (GTA VI specific updates) and `gta_online` (weekly event weeks, discounts, podium vehicles).
- **Article Enrichment**: Extracts OpenGraph editorial summaries and event rewards (Lucky Wheel Podium Vehicle, LS Car Meet Prize Ride, 2x/3x cash bonuses).
- **Self-Healing Background Scheduler**: Built-in `APScheduler` asynchronously syncs with Rockstar every 15 minutes.
- **Zero-Config Database**: Persistent asynchronous SQLite storage (`aiosqlite`) with zero external DB dependencies required to get started.
- **Production Ready**: Includes `Dockerfile`, `docker-compose.yml`, health check probes (`/health`), and test suites (`pytest`).

---

## 🏛️ System Architecture

```
Rockstar GraphQL & Newswire
            │
            ▼
┌───────────────────────────────┐
│         ViceWire API          │
│  - Rockstar GraphQL Ingester  │
│  - Article Enrichment Engine  │
│  - 15-Minute Async Scheduler  │
│  - SQLite Storage (aiosqlite) │
│  - FastAPI REST Endpoints     │
└───────────────┬───────────────┘
                │ REST API
                ▼
┌───────────────────────────────┐
│     Downstream Consumers      │
│  - Telegram Bot (External)    │
│  - Discord Webhooks           │
│  - Web / Mobile Frontends     │
└───────────────────────────────┘
```

For complete technical design, see the [Architecture Documentation](docs/ARCHITECTURE.md).

---

## 🚀 Quick Start

### Option A: Running with Docker Compose (Recommended)

```bash
# 1. Clone repository
git clone <your-repo-url>
cd <your-repo-name>

# 2. Copy environment template
cp .env.example .env

# 3. Start service
docker compose up -d --build
```
Your API is now running at `http://localhost:8000`.

### Option B: Running Locally

```bash
# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment configuration
cp .env.example .env

# 4. Start API server
python -m app.main
```

---

## 📖 API Reference Summary

Interactive Swagger documentation is available at **`http://localhost:8000/docs`**.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Service health status & sitemap |
| `GET` | `/health` | Container liveness & readiness probe |
| `GET` | `/api/v1/news` | All news with pagination (`page`, `limit`), search (`search`), and category filter (`category`) |
| `GET` | `/api/v1/news/gta6` | Shortcut for GTA 6 announcements & trailers |
| `GET` | `/api/v1/news/online` | Shortcut for GTA Online updates |
| `GET` | `/api/v1/news/{article_id}` | Detailed single article view |
| `GET` | `/api/v1/weekly/current` | Active GTA Online event week bonuses & vehicle rewards |
| `GET` | `/api/v1/weekly/history` | Past event weeks history |
| `POST` | `/api/v1/sync` | Manually trigger an immediate sync from Rockstar |
| `GET` | `/api/v1/sync/status` | DB metrics (total articles, breakdown by category) |

For complete schemas and response examples, refer to [API Reference](docs/API_REFERENCE.md).

---

## 🧪 Testing

Run the automated test suite:
```bash
source .venv/bin/activate
pytest tests/
```

---

## 📁 Repository Structure

```
├── app/
│   ├── main.py                  # Application entry point & lifespan
│   ├── core/                    # Config & database initialization
│   ├── models/                  # Pydantic request/response schemas
│   ├── services/                # Rockstar GraphQL client, enricher, scheduler
│   └── api/routes/              # News, weekly events, and sync routes
├── .agent/                      # Guidelines & task backlog for AI developers
│   ├── README.md                # Fast orientation & navigation index
│   ├── instructions.md          # Operational rules for coding agents
│   ├── ARCHITECTURE_GUIDE.md
│   ├── CONVENTIONS.md
│   └── TASKS.md
├── docs/                        # Complete technical documentation
│   ├── ARCHITECTURE.md
│   ├── API_REFERENCE.md
│   └── DEPLOYMENT.md
├── tests/                       # Pytest test suite
├── Dockerfile                   # Production container definition
├── docker-compose.yml           # Multi-container / standalone orchestration
├── requirements.txt             # Python package dependencies
└── README.md
```

---

## 🤖 For AI Developers & Contributors

If you are using an AI coding agent to extend this repository, direct the agent to read:
- **`.agent/README.md`**: Overview & navigation guide for AI agents.
- **`.agent/instructions.md`**: Operational rules and checklist.
- **`.agent/ARCHITECTURE_GUIDE.md`**: Upstream GraphQL patterns and design rationale.
- **`.agent/CONVENTIONS.md`**: Async guidelines and coding standards.
- **`.agent/TASKS.md`**: Prioritized roadmap for upcoming features.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
