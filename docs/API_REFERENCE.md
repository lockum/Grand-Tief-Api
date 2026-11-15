# API Reference Specification

Base URL: `http://localhost:8000` or your production domain.  
All news and event endpoints are mounted under `/api/v1`.

Interactive Swagger UI: `/docs`  
ReDoc UI: `/redoc`

---

## 1. System Endpoints

### `GET /`
Returns the operational status and list of available top-level resource links.

#### Response `200 OK`
```json
{
  "service": "ViceWire API",
  "status": "online",
  "version": "1.0.0",
  "docs_url": "/docs",
  "endpoints": {
    "all_news": "/api/v1/news",
    "gta6_news": "/api/v1/news/gta6",
    "online_news": "/api/v1/news/online",
    "current_weekly_event": "/api/v1/weekly/current",
    "sync_status": "/api/v1/sync/status",
    "health": "/health"
  }
}
```

---

### `GET /health`
Liveness and readiness health probe used by Docker, Kubernetes, and reverse proxies.

#### Response `200 OK`
```json
{
  "status": "healthy",
  "database": "connected",
  "scheduler_running": true
}
```

---

## 2. News Endpoints

### `GET /api/v1/news`
Fetches a paginated list of news articles with optional category and keyword filtering.

#### Query Parameters
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `category` | string | No | `null` | Filter by `gta6`, `gta_online`, or `rockstar` |
| `search` | string | No | `null` | Case-insensitive keyword search in title & summary |
| `page` | integer | No | `1` | Page number (min: 1) |
| `limit` | integer | No | `10` | Results per page (min: 1, max: 50) |

#### Response `200 OK`
```json
{
  "total": 21,
  "page": 1,
  "limit": 2,
  "results": [
    {
      "id": "89834o94713o21",
      "title": "Pre-Load Grand Theft Auto VI Now",
      "slug": "pre-load-grand-theft-auto-vi-now",
      "url": "https://www.rockstargames.com/newswire/article/89834o94713o21/pre-load-grand-theft-auto-vi-now",
      "image_url": "https://media-rockstargames-com.akamaized.net/tina-uploads/posts/89834o94713o21/94f09130d07de4a50e3ab971e2b7d8c253b7c706.jpg",
      "summary": "Pre-loading is now available for everyone who has pre-ordered Grand Theft Auto VI digitally.",
      "category": "gta6",
      "tags": ["Grand Theft Auto VI"],
      "published_at": "11/10/26, 3:00 PM",
      "is_weekly_event": false,
      "created_at": "2026-11-15 00:45:34",
      "notified": false
    }
  ]
}
```

---

### `GET /api/v1/news/gta6`
Convenience shortcut for `GET /api/v1/news?category=gta6`.

#### Query Parameters
- `page` (int, default: 1)
- `limit` (int, default: 10, max: 50)

---

### `GET /api/v1/news/online`
Convenience shortcut for `GET /api/v1/news?category=gta_online`.

#### Query Parameters
- `page` (int, default: 1)
- `limit` (int, default: 10, max: 50)

---

### `GET /api/v1/news/{article_id}`
Retrieves a single article by its Rockstar hash ID.

#### Path Parameters
- `article_id` (string, required): e.g. `89834o94713o21`

#### Error Response `404 Not Found`
```json
{
  "detail": "Article not found"
}
```

---

## 3. Weekly Events Endpoints

### `GET /api/v1/weekly/current`
Returns the active GTA Online event week bonuses, podium vehicle, and discounts.

#### Response `200 OK`
```json
{
  "id": 1,
  "article_id": "178a115o743442",
  "title": "GTA+ Members Can Now Claim a Free Grotti Itali RSX",
  "url": "https://www.rockstargames.com/newswire/article/178a115o743442/gta-members-can-now-claim-a-free-grotti-itali-rsx",
  "summary": "Get ahead of the impending holiday rush with a Grotti Itali RSX sports car, free to claim for GTA+ Members from The Vinewood Car Club showroom.",
  "bonuses": [
    "2x GTA$ & RP on High-Value Heist Targets",
    "3x Rewards on Community Series"
  ],
  "discounts": [
    "40% off Mammoth F-160 Raiju",
    "30% off Grotti Itali RSX"
  ],
  "podium_vehicle": "Pegassi Zentorno",
  "prize_ride": "Annis Elegy RH8",
  "created_at": "2026-11-15 00:45:34"
}
```

---

### `GET /api/v1/weekly/history`
Returns past event weeks with pagination.

#### Query Parameters
- `limit` (int, default: 10, max: 50)

---

## 4. Synchronization Endpoints

### `POST /api/v1/sync`
Manually triggers an immediate pull from Rockstar Games GraphQL endpoints and stores new/updated articles.

#### Response `200 OK`
```json
{
  "new_articles_count": 0,
  "updated_articles_count": 21,
  "message": "Sync successful. Ingested 0 new articles, updated 21.",
  "synced_at": "2026-11-15T00:52:00.123456Z"
}
```

---

### `GET /api/v1/sync/status`
Returns metrics and dataset volume.

#### Response `200 OK`
```json
{
  "status": "healthy",
  "total_articles": 21,
  "gta6_articles": 15,
  "gta_online_articles": 6,
  "weekly_events_tracked": 3,
  "latest_article_published_at": "11/10/26, 3:00 PM",
  "checked_at": "2026-11-15T00:52:00.123456Z"
}
```

