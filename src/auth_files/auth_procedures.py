"""
Module for authentication procedures in the FastAPI application.
"""

from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import timedelta
from sqlalchemy.orm import Session
from src.routes.jwt import create_refresh_token, verify_token
from src.auth_files.auth_settings import SECRET_KEY, ALGORITHM
from src.db.db import get_db
from src.db.models import User
from src.routes.jwt import create_access_token

app = FastAPI()

router = APIRouter(prefix='/contacts')

ACCESS_TOKEN_EXPIRE_MINUTES = 20

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(email: str, password: str, session: Session = Depends(get_db)):
    """
    Get user based on email and password.

    :param email: User's email
    :type email: str
    :param password: User's password
    :type password: str
    :param session: SQLAlchemy database session
    :type session: sqlalchemy.orm.Session
    :return: User if found, None otherwise
    :rtype: src.db.models.User | None
    """
    user = session.query(User).filter(User.email == email).first()
    if user and pwd_context.verify(password, user.hashed_password):
        return user
    return None


@app.post("/token/")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint to generate access and refresh tokens.

    :param form_data: Form data containing username and password
    :type form_data: OAuth2PasswordRequestForm
    :return: Dictionary containing access token, token type, and refresh token
    :rtype: dict
    """
    user = get_user(form_data.username, form_data.password)
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
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


@app.post("/token/refresh/")
def refresh_access_token(current_token: str = Depends(oauth2_scheme)):
    """
    Refresh token endpoint.

    :param current_token: Current refresh token
    :type current_token: str
    :return: Dictionary containing refreshed access token and token type
    :rtype: dict
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = verify_token(current_token)
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refreshed_token = create_access_token(data={"sub": sub}, expires_delta=access_token_expires)

    return {"access_token": refreshed_token, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Get the current user based on the provided token.

    :param token: Access token
    :type token: str
    :param db: SQLAlchemy database session
    :type db: sqlalchemy.orm.Session
    :return: Current user
    :rtype: src.db.models.User
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload["sub"]
        if email is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception

    user: User = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


def get_active_user(current_user: User = Depends(get_current_user)):
    """
    Get the active user.

    :param current_user: Current user obtained from get_current_user
    :type current_user: src.db.models.User
    :return: Current user
    :rtype: src.db.models.User
    """
    if current_user is None:
        raise HTTPException(status_code=400, detail="There is no active user")
    return current_user


def verify_user_email(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Verify user's email based on the provided token.

    :param token: Access token
    :type token: str
    :param db: SQLAlchemy database session
    :type db: sqlalchemy.orm.Session
    :return: Dictionary containing success message and status code
    :rtype: dict
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload["sub"]
        if email is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception

    user: User = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    if not user.is_verified:
        user.is_verified = True
        db.commit()

    return {"message": "Email verification successful!", "status_code": status.HTTP_200_OK}
