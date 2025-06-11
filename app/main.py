from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

import app.api.v1.websockets.handlers
from app.api.v1.router import api_router
from app.clients.redis_client import close_redis_connections
from app.core.config import settings
from app.core.starters import initialize_app
from app.utils.websocket.redis_listener import stop_redis_listener


class ProxyHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle proxy headers from NGINX reverse proxy.
    This ensures that FastAPI recognizes HTTPS requests when behind a reverse proxy.
    """

    async def dispatch(self, request: Request, call_next):
        if settings.TRUST_PROXY_HEADERS:
            # Check for X-Forwarded-Proto header from NGINX
            forwarded_proto = request.headers.get("X-Forwarded-Proto")
            if forwarded_proto:
                # Update the request scope to reflect the original protocol
                request.scope["scheme"] = forwarded_proto

            # Check for X-Forwarded-Host header
            forwarded_host = request.headers.get("X-Forwarded-Host")
            if forwarded_host:
                request.scope["server"] = (forwarded_host, None)

            # Check for X-Forwarded-Port header
            forwarded_port = request.headers.get("X-Forwarded-Port")
            if forwarded_port and forwarded_host:
                try:
                    port = int(forwarded_port)
                    request.scope["server"] = (forwarded_host, port)
                except ValueError:
                    pass  # Invalid port, ignore

        response = await call_next(request)
        return response


@asynccontextmanager
async def lifespan(_: FastAPI):

    await initialize_app()
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

# Set up proxy headers middleware (must be first)
app.add_middleware(ProxyHeadersMiddleware)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
