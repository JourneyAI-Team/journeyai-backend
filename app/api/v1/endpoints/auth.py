from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.token import Token

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    Obtain a bearer access token.

    This endpoint is OAuth 2 compatible.
    The user's credentials are validated and, if correct, a JWT token
    is issued.

    Parameters
    ----------
    form_data : OAuth2PasswordRequestForm, optional
        Form that contains the user's e-mail (as *username*) and
        password. Injected automatically by FastAPI.

    Returns
    -------
    dict
        Dictionary with two keys:
        ``access_token`` – the generated JWT.
        ``token_type`` – always ``"bearer"``.

    Raises
    ------
    HTTPException
        401 if the credentials are invalid.
    """
    user = await User.find_one(User.email == form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            subject=str(user.id), expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/register", response_model=Token)
async def register(
    # User creation schema should be added here, e.g. `user_in: UserCreate`
) -> Any:
    """
    Register a new user.

    Parameters
    ----------
    user_in : UserCreate
        Pydantic model with the data required to create a new user.
        (Placeholder - replace with the actual schema once available.)

    Returns
    -------
    dict
        Same structure as the login endpoint:
        ``access_token`` and ``token_type`` on successful registration.

    Notes
    -----
    This endpoint has not yet been implemented.
    """
    # Implementation here


@router.get("/me", response_model=Any)
async def get_me(current_user: User = Depends(get_current_user)) -> Any:
    """
    Retrieve the currently authenticated user.

    Parameters
    ----------
    current_user : User, optional
        The user resolved from the provided JWT. Supplied via the
        ``get_current_user`` dependency.

    Returns
    -------
    User
        The authenticated user object.
    """
    return current_user
