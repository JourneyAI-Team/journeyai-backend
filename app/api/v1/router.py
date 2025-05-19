from fastapi import APIRouter

from app.api.v1.endpoints import account, auth, session
from app.api.v1.websockets import endpoints as websocket_endpoints

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(account.router, prefix="/account", tags=["Account"])
api_router.include_router(session.router, prefix="/session", tags=["Session"])
api_router.include_router(websocket_endpoints.router, prefix="/ws", tags=["WebSockets"])
