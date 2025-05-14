from fastapi import APIRouter

from app.api.v1.endpoints import auth, conversations, customers, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(
    conversations.router, prefix="/conversations", tags=["Conversations"]
)
api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])

# Add more routers here as needed
