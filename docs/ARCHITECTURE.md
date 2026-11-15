# Architecture & System Design

## Overview

**ViceWire** is an asynchronous news ingestion engine and REST API designed to track, normalize, and serve official Grand Theft Auto VI news, GTA Online updates, and weekly event bonuses.

It decouples the **upstream data collection layer** (Rockstar Games' official GraphQL gateway and OpenGraph scrapers) from consumer applications (such as Telegram bots, Discord bots, web dashboards, or mobile widgets).

---

## High-Level Topology

```
                  ┌─────────────────────────────────────────┐
                  │          Rockstar Games Sources         │
                  │  - graph.rockstargames.com (GraphQL)    │
                  │  - rockstargames.com/newswire (HTML/OG) │
                  └────────────────────┬────────────────────┘
                                       │ HTTPS / JSON
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │              ViceWire API               │
                  │                                         │
                  │  ┌───────────────────────────────────┐  │
                  │  │        Ingestion Engine           │  │
                  │  │  - RockstarApiClient              │  │
                  │  │  - ArticleEnricher (OG / Bonuses) │  │
                  │  │  - Synchronizer (Deduplication)   │  │
                  │  └─────────────────┬─────────────────┘  │
                  │                    │                    │
                  │  ┌─────────────────▼─────────────────┐  │
                  │  │       Async SQLite Storage        │  │
                  │  │  - articles (indexed by category) │  │
                  │  │  - weekly_events (bonuses/rewards)│  │
                  │  └─────────────────┬─────────────────┘  │
                  │                    │                    │
                  │  ┌─────────────────▼─────────────────┐  │
                  │  │           FastAPI Server          │  │
                  │  │  - /api/v1/news                   │  │
                  │  │  - /api/v1/weekly                 │  │
                  │  │  - /api/v1/sync                   │  │
                  │  └─────────────────┬─────────────────┘  │
                  └────────────────────┼────────────────────┘
                                       │ REST / JSON
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │           Downstream Consumers          │
                  │  - Telegram Bot (Separate Repository)   │
                  │  - Discord Webhooks                     │
                  │  - Web Frontends / Mobile Dashboards    │
                  └─────────────────────────────────────────┘
```

---

## Core Components

### 1. Ingestion Engine (`app/services/rockstar_api.py`)
- Interfaces directly with `https://graph.rockstargames.com/`.
- Executes the `NewswireList` GraphQL query with parameterized tag filters:
  - `tagIdHash: "vi"`: Grand Theft Auto VI news, trailers, launch galleries, music, and pre-load announcements.
  - `tagIdHash: "gta-online"`: GTA Online weekly event weeks, GTA+ member perks, and updates.
  - `tagIdHash: None`: General Rockstar Games company updates and newswire feed.
- Extracts `id_hash`, `url`, `title`, `created_formatted`, `preview_images_parsed` (Akamai CDN image assets), and tag taxonomies.

### 2. Article Enrichment (`app/services/article_parser.py`)
- When a new post ID is detected, the enricher fetches the canonical article page (`https://www.rockstargames.com/newswire/article/{id}/{slug}`).
- Extracts:
  - `og:description` for an accurate editorial summary.
  - Lucky Wheel **Podium Vehicle** names.
  - LS Car Meet **Prize Ride** challenges and vehicle names.
  - Multiplier bonuses (2x/3x GTA$ & RP) and vehicle/property discounts.

### 3. Background Scheduler (`app/services/scheduler.py`)
- Managed by `APScheduler` (`AsyncIOScheduler`) attached to FastAPI's lifespan lifecycle.
- Runs non-blocking sync cycles every `POLL_INTERVAL_MINUTES` (default: 15 minutes).
- Gracefully starts on application boot and shuts down without leaving open connection handles.

### 4. Database & Storage (`app/core/database.py`)
- Uses asynchronous SQLite via `aiosqlite`.
- **`articles` Table**:
  - `id` (TEXT PRIMARY KEY): Unique hash from Rockstar.
  - `title` (TEXT): Cleaned article title.
  - `slug` (TEXT): URL slug.
  - `url` (TEXT): Canonical link to full article on Rockstar Games.
  - `image_url` (TEXT): High-resolution Akamai CDN banner image.
  - `summary` (TEXT): Editorial description.
  - `category` (TEXT): Indexed enum-like string (`gta6`, `gta_online`, `rockstar`).
  - `tags` (TEXT): JSON array of primary and secondary tags.
  - `published_at` (TEXT): Publication timestamp.
  - `is_weekly_event` (INTEGER): Flag (1/0) indicating weekly bonus article.
  - `notified` (INTEGER): Flag for downstream notification engines (0 = new, 1 = announced).
- **`weekly_events` Table**:
  - `id` (INTEGER PRIMARY KEY AUTOINCREMENT).
  - `article_id` (TEXT UNIQUE): Foreign key to `articles.id`.
  - `title` (TEXT).
  - `url` (TEXT).
  - `summary` (TEXT).
  - `bonuses` (TEXT): JSON array of bonuses.
  - `discounts` (TEXT): JSON array of discounted vehicles and properties.
  - `podium_vehicle` (TEXT): Lucky wheel vehicle.
  - `prize_ride` (TEXT): Car meet prize vehicle.

