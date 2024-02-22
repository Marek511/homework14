"""
Module defining API endpoints related to user authentication and profile management with FastAPI.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import timedelta
from src.routes.jwt import create_access_token, create_refresh_token, update_user_avatar
from src.auth_files.auth_procedures import get_current_user, get_user
from src.db.db import get_db
from src.db.models import User
import cloudinary
import cloudinary.uploader

app = FastAPI()

ACCESS_TOKEN_EXPIRE_MINUTES = 20

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
def signup(user: User, db: Session = Depends(get_db)):
    """
    Endpoint to register a new user.

    Args:
        user (User): User registration data.
        db (Session, optional): SQLAlchemy session. Defaults to Depends(get_db).

    Returns:
        dict: Response message and status code.
    """
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")
    hashed_password = pwd_context.hash(user.password)
    db_user = User(email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"user": db_user, "message": "User signed up successfully!", "status_code": status.HTTP_201_CREATED}


@app.post("/login", response_model=dict)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Endpoint to authenticate and log in a user.

    Args:
        form_data (OAuth2PasswordRequestForm, optional): OAuth2 password request form. Defaults to Depends().
        db (Session, optional): SQLAlchemy session. Defaults to Depends(get_db).

    Returns:
        dict: Response with access token, refresh token, message, and status code.
    """
    user = get_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_data = {"sub": user.email}
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data=refresh_token_data)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "message": "User logged in successfully!",
        "status_code": status.HTTP_200_OK
    }


@app.get("/secret")
def read_secret(current_user: User = Depends(get_current_user)):
    """
    Endpoint to access a secret information.

    Args:
        current_user (User, optional): Current user obtained from authentication. Defaults to Depends(get_current_user).

    Returns:
        dict: Response message with user's email.
    """
    return {"message": "You have access to this secret information!", "user_email": current_user.email}


@app.put("/user/avatar")
def update_avatar(avatar_url: str, current_user: User = Depends(get_current_user)):
    """
    Endpoint to update user's avatar.

    Args:
        avatar_url (str): URL of the new avatar image.
        current_user (User, optional): Current user obtained from authentication. Defaults to Depends(get_current_user).

    Returns:
        dict: Response message and status code.
    """
    cloudinary_response = cloudinary.uploader.upload(avatar_url)
    updated_avatar_url = cloudinary_response.get("url")

    update_user_avatar(current_user.id, avatar_url)
    return {"message": "Avatar updated successfully!", "status_code": status.HTTP_200_OK}
