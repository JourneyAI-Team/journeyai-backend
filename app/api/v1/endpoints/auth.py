from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password

from app.models.user import User
from app.models.organization import Organization

from app.schemas.token import Token
from app.schemas.user import UserCreate, UserRead

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
        ``access_token`` - the generated JWT.
        ``token_type`` - always ``"bearer"``.

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
async def register(user_in: UserCreate) -> Any:
    """
    Register a new user.

    Parameters
    ----------
    user_in : UserCreate
        Pydantic model with the data required to create a new user.

    Returns
    -------
    dict
        Same structure as the login endpoint:
        ``access_token`` and ``token_type`` on successful registration.

    Raises
    ------
    HTTPException
        400 if a user with the same email already exists.
    """

    # Check if user already exists
    existing_user = await User.find_one(User.email == user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user
    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password)
    )
    
    org_domain = user_in.email.split("@")[1]
    org_name = org_domain.split(".")[0]

    organization = await Organization.find_one(Organization.name == org_name)

    # If organization does not exist, create a new organization with the owner id as the new user's id
    if not organization:
        organization = Organization(
            name = org_name,
            domain = org_domain,
            owner_id = new_user.id
        )

        await organization.insert()

    # Assign the new user to its organization
    new_user.organization_id = organization.id

    # Save user to database
    await new_user.insert()

    # Generate access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(new_user.id), expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserRead)
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
    UserRead
        The authenticated user object with sensitive information removed.
    """
    return current_user
