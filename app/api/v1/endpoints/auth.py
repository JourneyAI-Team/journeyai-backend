import uuid
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.organization import Organization
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserApiKey, UserCreate, UserRead

router = APIRouter()


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    description="""Obtain a bearer access token. \
        This endpoint is OAuth 2 compatible. \
        The user's credentials are validated and, if correct, a JWT token \
        is issued. """,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": " The credentials are invalid"}
    },
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
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

    # Generate api key for websockets auth and update the user's access token field using the new api key
    api_key = uuid.uuid4().hex
    await user.set({User.access_token: api_key})

    return {
        "access_token": create_access_token(
            subject=str(user.id), expires_delta=access_token_expires
        ),
        "api_key": api_key,
        "token_type": "bearer",
    }


@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    description="Register a new user.",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "User with the same email already exists."
        }
    },
)
async def register(user_in: UserCreate) -> Any:
    # Check if user already exists
    existing_user = await User.find_one(User.email == user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    new_user = User(
        email=user_in.email, hashed_password=get_password_hash(user_in.password)
    )

    org_domain = user_in.email.split("@")[1]
    org_name = org_domain.split(".")[0]

    organization = await Organization.find_one(Organization.name == org_name)

    # If organization does not exist, create a new organization with the owner id as the new user's id
    if not organization:
        organization = Organization(
            name=org_name, domain=org_domain, owner_id=new_user.id
        )

        await organization.insert()

    # Assign the new user to its organization
    new_user.organization_id = organization.id

    # Generate api key for websockets auth and save to user database
    api_key = uuid.uuid4().hex
    new_user.access_token = api_key

    try:
        # Save user to database
        await new_user.insert()

        # Generate access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=str(new_user.id), expires_delta=access_token_expires
        )
        logger.success(f"User registered successfully. {user_in.email}")
    except Exception as e:
        logger.exception(
            f"Database insert failed when registering user. {user_in.email}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error registering user.",
        ) from e
    return {
        "access_token": access_token,
        "api_key": api_key,
        "token_type": "bearer",
    }


@router.get(
    "/me",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    description="Retrieve the currently authenticated user.",
)
async def get_me(current_user: User = Depends(get_current_user)) -> Any:
    return current_user


@router.get(
    "/api-key",
    response_model=UserApiKey,
    status_code=status.HTTP_200_OK,
    description="Retrieve the currently authenticated user's API key.",
)
async def get_api_key(current_user: User = Depends(get_current_user)) -> UserApiKey:
    return UserApiKey(api_key=current_user.access_token)
