from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError

from app.core.config import settings
from app.models.user import User
from app.schemas.token import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Retrieve the current user from a JWT token.

    Parameters
    ----------
    token : str
        The JSON Web Token supplied by the request via the OAuth2
        password bearer flow.

    Returns
    -------
    User
        The authenticated user instance.

    Raises
    ------
    HTTPException
        If the token is invalid or the corresponding user does not exist.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    user = await User.get(token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ensure the current user is active.

    Parameters
    ----------
    current_user : User
        The user instance retrieved from `get_current_user`.

    Returns
    -------
    User
        The same user instance if active.

    Raises
    ------
    HTTPException
        If the user account is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Validate that the current user has administrative privileges.

    Parameters
    ----------
    current_user : User
        The user instance validated by `get_current_active_user`.

    Returns
    -------
    User
        The same user instance if they have admin rights.

    Raises
    ------
    HTTPException
        If the user lacks administrative permissions.
    """

    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    return current_user
