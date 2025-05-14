from typing import Any, List

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_active_user, get_current_admin_user
from app.core.security import get_password_hash
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[Any])
async def list_users(
    current_user: User = Depends(get_current_admin_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    List users (admin only)
    
    Args:
        current_user: Current admin user
        skip: Number of users to skip
        limit: Maximum number of users to return
        
    Returns:
        List of users
    """
    users = await User.find_all().skip(skip).limit(limit).to_list()
    return users


@router.get("/me", response_model=Any)
async def get_user_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user information
    """
    return current_user


@router.put("/me", response_model=Any)
async def update_user_me(
    # Add user update schema
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update current user
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Updated user information
    """
    # Implementation
    pass 