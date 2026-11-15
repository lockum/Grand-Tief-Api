import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db, get_db
from app.services.scheduler import start_scheduler, stop_scheduler, scheduler
from app.services.synchronizer import sync_all_news
from app.api.routes import news, weekly, sync

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("vicewire")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup phase
    logger.info("Initializing database...")
    await init_db()

    # Initial sync from Rockstar
    logger.info("Performing initial news synchronization...")
    try:
        await sync_all_news()
    except Exception as e:
        logger.warning(f"Initial sync warning: {e}")

    # Start background scheduler
    start_scheduler()
    logger.info("Application startup complete.")

    yield

    # Shutdown phase
    logger.info("Shutting down background scheduler...")
    stop_scheduler()


tags_metadata = [
    {
        "name": "News",
        "description": "Endpoints to query and search official Rockstar Games, GTA VI, and GTA Online news.",
    },
    {
        "name": "GTA Online Weekly Events",
        "description": "Endpoints for weekly bonuses, vehicle rewards (podium, prize ride), and discounts.",
    },
    {
        "name": "Synchronization",
        "description": "Health checks, metrics, and manual synchronization triggers.",
    },
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "High-performance REST API service providing official Grand Theft Auto VI news, "
        "GTA Online updates, weekly event bonuses, and Rockstar Newswire tracking."
    ),
    version="1.0.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan
)

# CORS configuration for cross-origin frontend / bot integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception at {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please check server logs."}
    )


# Include routers
app.include_router(news.router, prefix=settings.API_V1_STR)
app.include_router(weekly.router, prefix=settings.API_V1_STR)
app.include_router(sync.router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Synchronization"])
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "status": "online",
        "version": "1.0.0",
        "docs_url": "/docs",
        "endpoints": {
            "all_news": f"{settings.API_V1_STR}/news",
            "gta6_news": f"{settings.API_V1_STR}/news/gta6",
            "online_news": f"{settings.API_V1_STR}/news/online",
            "current_weekly_event": f"{settings.API_V1_STR}/weekly/current",
            "sync_status": f"{settings.API_V1_STR}/sync/status",
            "health": "/health"
        }
    }


@app.get("/health", tags=["Synchronization"])
async def health_check():
    """Liveness and readiness probe for container orchestrators."""
    db_healthy = False
    try:
        async with get_db() as conn:
            cursor = await conn.execute("SELECT 1")
            row = await cursor.fetchone()
            if row and row[0] == 1:
                db_healthy = True
    except Exception as e:
        logger.error(f"Healthcheck DB failure: {e}")

    is_healthy = db_healthy
    status_code = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "healthy" if is_healthy else "unhealthy",
            "database": "connected" if db_healthy else "error",
            "scheduler_running": scheduler.running
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
