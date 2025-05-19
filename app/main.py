from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.init_db import init_db
from app.utils.loki_logger import setup_logger
from app.utils.redis_client import close_redis_connections
from app.utils.websocket.redis_listener import start_redis_listener, stop_redis_listener

import app.api.v1.websockets.handlers


@asynccontextmanager
async def lifespan(_: FastAPI):

    if settings.LOKI_URL:

        setup_logger(
            settings.LOKI_URL,
            labels={"job": "journey", "environment": settings.ENVIRONMENT},
        )

    await init_db()

    # Start Redis listener for WebSocket messages
    await start_redis_listener()

    yield

    # Stop Redis listener when shutting down
    await stop_redis_listener()

    # Close Redis connections
    await close_redis_connections()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="JourneyAI",
    version="0.1.0",
    lifespan=lifespan,
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health Check"])
async def health_check():
    """
    Health check endpoint

    Returns:
        dict: Status message indicating the API is running
    """

    return {"status": "ok", "message": "JourneyAI API is running"}


# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
