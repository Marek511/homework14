"""
Module defining database-related functions for user operations.
"""

from libgravatar import Gravatar
from sqlalchemy.orm import Session
from src.db.models import User
from src.schemas import UserModel


def get_user_by_email(email: str, db: Session) -> User:
    """
    Retrieve a user by their email from the database.

    Args:
        email (str): User's email.
        db (Session): SQLAlchemy session.

    Returns:
        User: User object retrieved from the database.
    """
    return db.query(User).filter(User.email == email).first()


def create_user(body: UserModel, db: Session) -> User:
    """
    Create a new user in the database.

    Args:
        body (UserModel): User data.
        db (Session): SQLAlchemy session.

    Returns:
        User: Newly created user object.
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Update the refresh token for a user in the database.

    Args:
        user (User): User object.
        token (str | None): Refresh token.
        db (Session): SQLAlchemy session.

    Returns:
        None
    """
    user.refresh_token = token
    db.commit()


async def confirm_email(email: str, db: Session) -> None:
    """
    Confirm a user's email in the database.

    Args:
        email (str): User's email.
        db (Session): SQLAlchemy session.

    Returns:
        None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    Update the avatar URL for a user in the database.

    Args:
        email (str): User's email.
        url (str): New avatar URL.
        db (Session): SQLAlchemy session.

    Returns:
        User: Updated user object.
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
