from fastapi import APIRouter

from app.api.v1.endpoints import (
    account,
    artifact,
    assistant,
    auth,
    message,
    profile,
    session,
)
from app.api.v1.websockets import endpoints as websocket_endpoints

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(account.router, prefix="/account", tags=["Account"])
api_router.include_router(profile.router, prefix="/profile", tags=["Profile"])
api_router.include_router(session.router, prefix="/session", tags=["Session"])
api_router.include_router(message.router, prefix="/message", tags=["Message"])
api_router.include_router(artifact.router, prefix="/artifact", tags=["Artifact"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["Assistant"])
api_router.include_router(websocket_endpoints.router, prefix="/ws", tags=["WebSockets"])
