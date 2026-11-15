# API Reference Specification

Base URL: `http://localhost:8000`  
All operational data endpoints are mounted under `/api/v1`.

Interactive Swagger UI: `http://localhost:8000/docs`  
ReDoc UI: `http://localhost:8000/redoc`

---

## Authentication (HTTP Basic Auth)

All data endpoints require **HTTP Basic Authentication**. You can authenticate requests via the standard `Authorization: Basic <base64>` header, `curl -u`, or using HTTP client libraries.

### Configured User Roles
| Role | Default Username | Default Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Read-Only** | `reader` | `vicewire_read_2026` | Access all news, searches, and weekly event data (`/api/v1/news`, `/api/v1/weekly`, `/api/v1/sync/status`). Used by Telegram bots, frontends, and external consumers. |
| **Admin** | `admin` | `vicewire_admin_2026` | Full access, including triggering manual synchronization (`POST /api/v1/sync`). |

*Credentials can be configured via environment variables in `.env` (`API_READONLY_USERNAME`, `API_READONLY_PASSWORD`, `API_ADMIN_USERNAME`, `API_ADMIN_PASSWORD`).*

---

## Testing Calls with cURL

```bash
# 1. Test public health check (No auth required)
curl -i http://localhost:8000/health

# 2. Get latest GTA 6 news (Read-Only user)
curl -i -u reader:vicewire_read_2026 http://localhost:8000/api/v1/news/gta6

# 3. Get active GTA Online weekly bonuses
curl -i -u reader:vicewire_read_2026 http://localhost:8000/api/v1/weekly/current

# 4. Trigger manual news sync (Admin only)
curl -i -X POST -u admin:vicewire_admin_2026 http://localhost:8000/api/v1/sync
```

---

## Python Consumer Example (For Telegram Bot)

```python
import httpx

API_BASE_URL = "http://localhost:8000/api/v1"
AUTH = ("reader", "vicewire_read_2026")

async def get_gta6_news():
    async with httpx.AsyncClient(base_url=API_BASE_URL, auth=AUTH) as client:
        resp = await client.get("/news/gta6", params={"limit": 5})
        resp.raise_for_status()
        return resp.json()["results"]

async def get_weekly_event():
    async with httpx.AsyncClient(base_url=API_BASE_URL, auth=AUTH) as client:
        resp = await client.get("/weekly/current")
        resp.raise_for_status()
        return resp.json()
```

---

## Endpoints

### 1. System Endpoints
| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Public | Service index and sitemap |
| `GET` | `/health` | Public | Container and database healthcheck probe |

### 2. News Endpoints (Read-Only or Admin)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/news` | All news with pagination (`page`, `limit`), search (`search`), and category filter (`category`) |
| `GET` | `/api/v1/news/gta6` | Shortcut for GTA 6 announcements & trailers |
| `GET` | `/api/v1/news/online` | Shortcut for GTA Online updates |
| `GET` | `/api/v1/news/{article_id}` | Detailed single article view |

### 3. Weekly Events Endpoints (Read-Only or Admin)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/weekly/current` | Active GTA Online event week bonuses & vehicle rewards |
| `GET` | `/api/v1/weekly/history` | Past event weeks history |

### 4. Synchronization Endpoints
| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/sync` | **Admin Only** | Trigger immediate sync from Rockstar |
| `GET` | `/api/v1/sync/status` | Read-Only or Admin | View database metrics & totals |
