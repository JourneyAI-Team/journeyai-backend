import datetime as dt
from typing import Any, Optional, Union

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[dt.timedelta] = None
) -> str:
    """
    Create a JWT access token.

    Parameters
    ----------
    subject : Union[str, Any]
        Token subject (usually the user ID).
    expires_delta : Optional[datetime.timedelta], optional
        Custom time delta after which the token should expire.
        If ``None``, the default value configured in
        ``settings.ACCESS_TOKEN_EXPIRE_MINUTES`` is used.

    Returns
    -------
    str
        Encoded JWT access token.
    """

    now = dt.datetime.now(dt.timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + dt.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against its hashed counterpart.

    Parameters
    ----------
    plain_password : str
        The raw password provided by the user.
    hashed_password : str
        The stored hashed password.

    Returns
    -------
    bool
        ``True`` if the passwords match, otherwise ``False``.
    """

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plain-text password.

    Parameters
    ----------
    password : str
        The raw password to hash.

    Returns
    -------
    str
        A BCrypt hashed version of the password.
    """
    return pwd_context.hash(password)
