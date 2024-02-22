"""
Module defining API routes and functions for user-related operations.
"""

from fastapi import HTTPException, Depends, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.db.db import get_db
from src.routes.router_endpoints import router
from src.schemas import UserResponse, UserModel, TokenModel, RequestEmail
from src.services import send_email


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    body: UserModel,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    repository_users=None,
    auth_service=None
):
    """
    Endpoint for user registration.

    Args:
        body (UserModel): User data.
        background_tasks (BackgroundTasks): Background tasks to run asynchronously.
        request (Request): FastAPI request object.
        db (Session): SQLAlchemy session.
        repository_users: Repository for user-related database operations.
        auth_service: Service for authentication-related operations.

    Returns:
        dict: User information and confirmation detail.
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}


@router.post("/login", response_model=TokenModel)
async def login(
    body: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    repository_users=None,
    auth_service=None
):
    """
    Endpoint for user login.

    Args:
        body (OAuth2PasswordRequestForm): User login credentials.
        db (Session): SQLAlchemy session.
        repository_users: Repository for user-related database operations.
        auth_service: Service for authentication-related operations.

    Returns:
        dict: Access token and refresh token.
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db), auth_service=None, repository_users=None):
    """
    Endpoint to confirm user's email.

    Args:
        token (str): Email confirmation token.
        db (Session): SQLAlchemy session.
        auth_service: Service for authentication-related operations.
        repository_users: Repository for user-related database operations.

    Returns:
        dict: Confirmation message.
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed", "status_code": status.HTTP_200_OK}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db), repository_users=None):
    """
    Endpoint to request email confirmation.

    Args:
        body (RequestEmail): Email request data.
        background_tasks (BackgroundTasks): Background tasks to run asynchronously.
        request (Request): FastAPI request object.
        db (Session): SQLAlchemy session.
        repository_users: Repository for user-related database operations.

    Returns:
        dict: Confirmation message.
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed", "status_code": status.HTTP_200_OK}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}
