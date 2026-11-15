import pytest
import httpx
from app.core.config import settings

pytestmark = pytest.mark.asyncio

READONLY_AUTH = (settings.API_READONLY_USERNAME, settings.API_READONLY_PASSWORD)
ADMIN_AUTH = (settings.API_ADMIN_USERNAME, settings.API_ADMIN_PASSWORD)


async def test_public_root_endpoint(async_client: httpx.AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"


async def test_public_health_check(async_client: httpx.AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


async def test_unauthorized_access(async_client: httpx.AsyncClient):
    response = await async_client.get("/api/v1/news")
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers


async def test_invalid_credentials(async_client: httpx.AsyncClient):
    response = await async_client.get("/api/v1/news", auth=("wronguser", "wrongpass"))
    assert response.status_code == 401


async def test_readonly_user_can_access_news(async_client: httpx.AsyncClient):
    response = await async_client.get("/api/v1/news", auth=READONLY_AUTH)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2


async def test_readonly_user_can_access_gta6(async_client: httpx.AsyncClient):
    response = await async_client.get("/api/v1/news/gta6", auth=READONLY_AUTH)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["results"][0]["category"] == "gta6"


async def test_readonly_user_can_access_weekly(async_client: httpx.AsyncClient):
    response = await async_client.get("/api/v1/weekly/current", auth=READONLY_AUTH)
    assert response.status_code == 200
    data = response.json()
    assert data["podium_vehicle"] == "Pegassi Zentorno"


async def test_readonly_user_forbidden_from_admin_sync(async_client: httpx.AsyncClient):
    response = await async_client.post("/api/v1/sync", auth=READONLY_AUTH)
    assert response.status_code == 403
    assert "Admin privileges required" in response.json()["detail"]


async def test_admin_user_can_access_sync_status(async_client: httpx.AsyncClient):
    response = await async_client.get("/api/v1/sync/status", auth=ADMIN_AUTH)
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


async def test_get_article_by_id(async_client: httpx.AsyncClient):
    response = await async_client.get("/api/v1/news/test-gta6-1", auth=READONLY_AUTH)
    assert response.status_code == 200
    assert response.json()["id"] == "test-gta6-1"


async def test_get_article_not_found(async_client: httpx.AsyncClient):
    response = await async_client.get("/api/v1/news/non-existent-id", auth=READONLY_AUTH)
    assert response.status_code == 404
