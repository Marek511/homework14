"""
Module defining Pydantic models for the application.
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class ContactModel(BaseModel):
    """
    Pydantic model representing the structure of a contact.

    Attributes:
        name (str): First name of the contact.
        last_name (str): Last name of the contact.
        email (EmailStr): Email address of the contact.
        phone_no (str): Phone number of the contact.
        date_of_birth (date): Date of birth of the contact.
        description (Optional[str]): Additional description of the contact (default is an empty string).
    """
    name: str
    last_name: str
    email: EmailStr
    phone_no: str
    date_of_birth: date
    description: Optional[str] = ""


class UserModel(BaseModel):
    """
    Pydantic model representing the structure of a user during registration.

    Attributes:
        username (str): Username of the user (length between 5 and 10 characters).
        email (str): Email address of the user.
        password (str): Password of the user (length between 8 and 15 characters).
    """
    username: str = Field(min_length=5, max_length=10)
    email: str
    password: str = Field(min_length=8, max_length=15)


class UserDb(BaseModel):
    """
    Pydantic model representing the structure of a user retrieved from the database.

    Attributes:
        id (int): User ID.
        username (str): Username of the user.
        email (str): Email address of the user.
        created_at (datetime): Date and time when the user was created.
        avatar (str): URL of the user's avatar.

    Config:
        orm_mode (bool): Enable ORM mode for proper serialization of SQLAlchemy objects.
    """
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    """
    Pydantic model representing the response after user registration.

    Attributes:
        user (UserDb): User information.
        detail (str): Success message (default is "User successfully created").
    """
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    """
    Pydantic model representing the structure of a token.

    Attributes:
        access_token (str): Access token.
        refresh_token (str): Refresh token.
        token_type (str): Token type (default is "bearer").
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    """
    Pydantic model representing the structure of a request for email confirmation.

    Attributes:
        email (EmailStr): Email address for confirmation.
    """
    email: EmailStr
