"""
Module defining functions related to authentication, token creation, and user profile updates.
"""

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.auth_files.auth_settings import SECRET_KEY, ALGORITHM, oauth2_scheme
from src.db.db import get_db
from src.db.models import User

REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Create an access token.

    Args:
        data (dict): Payload data for the token.
        expires_delta (timedelta, optional): Token expiration time delta. Defaults to None.

    Returns:
        str: Encoded JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    """
    Create a refresh token.

    Args:
        data (dict): Payload data for the token.

    Returns:
        str: Encoded JWT refresh token.
    """
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    data.update({"exp": expire})
    refresh_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return refresh_token


def verify_token(token: str = Depends(oauth2_scheme)):
    """
    Verify the provided token.

    Args:
        token (str, optional): Token to be verified. Defaults to Depends(oauth2_scheme).

    Raises:
        HTTPException: Raised for invalid credentials.

    Returns:
        dict: Decoded token payload.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise credentials_exception


def update_user_avatar(user_id: int, avatar_url: str, db: Session = Depends(get_db)):
    """
    Update user avatar in the database.

    Args:
        user_id (int): User ID.
        avatar_url (str): New avatar URL.
        db (Session, optional): SQLAlchemy session. Defaults to Depends(get_db).

    Raises:
        HTTPException: Raised if the user is not found.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.avatar = avatar_url
        db.commit()
        db.refresh(user)
    else:
        raise HTTPException(status_code=404, detail="User not found")
