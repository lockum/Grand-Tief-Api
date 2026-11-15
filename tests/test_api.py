import pytest
import httpx

pytestmark = pytest.mark.asyncio


async def test_root_endpoint(async_client: httpx.AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "endpoints" in data


async def test_health_check(async_client: httpx.AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


async def test_get_all_news(async_client: httpx.AsyncClient):
    response = await async_client.get("/api/v1/news")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    assert len(data["results"]) >= 2


async def test_get_gta6_news(async_client: httpx.AsyncClient):
    response = await async_client.get("/api/v1/news/gta6")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["results"][0]["category"] == "gta6"
    assert len(data["results"][0]["title"]) > 0


async def test_get_online_news(async_client: httpx.AsyncClient):
    response = await async_client.get("/api/v1/news/online")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["results"][0]["category"] == "gta_online"


async def test_get_article_by_id(async_client: httpx.AsyncClient):
    response = await async_client.get("/api/v1/news/test-gta6-1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-gta6-1"
    assert data["title"] == "GTA VI Trailer Released"


async def test_get_article_not_found(async_client: httpx.AsyncClient):
    response = await async_client.get("/api/v1/news/non-existent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Article not found"


async def test_get_current_weekly_event(async_client: httpx.AsyncClient):
    response = await async_client.get("/api/v1/weekly/current")
    assert response.status_code == 200
    data = response.json()
    assert data["podium_vehicle"] == "Pegassi Zentorno"
    assert data["prize_ride"] == "Annis Elegy RH8"
    assert len(data["bonuses"]) > 0


async def test_sync_status(async_client: httpx.AsyncClient):
    response = await async_client.get("/api/v1/sync/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["total_articles"] >= 2
    assert data["gta6_articles"] >= 1
    assert data["gta_online_articles"] >= 1
