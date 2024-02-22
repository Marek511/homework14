"""
Module defining functionality for sending emails using FastAPI mail module.
"""

from pathlib import Path
from fastapi import FastAPI, BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config.config import settings

Base = declarative_base()

DATABASE_URL = settings.database_url
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class EmailSchema(BaseModel):
    """
    Pydantic model representing the email structure.

    Attributes:
        email (EmailStr): Email address of the recipient.
    """
    email: EmailStr


conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="Fast API",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)

app = FastAPI()


@app.post("/send-email")
def send_email(background_tasks: BackgroundTasks, body: EmailSchema):
    """
    Endpoint to send an email.

    Args:
        background_tasks (BackgroundTasks): FastAPI background tasks for asynchronous email sending.
        body (EmailSchema): Pydantic model representing the email structure.

    Returns:
        dict: Dictionary containing a success message.

    Example:
        {"message": "Email has been sent"}
    """
    message = MessageSchema(
        subject="Fastapi mail module",
        recipients=[body.email],
        template_body={"email.html"},
        subtype=MessageType.html
    )

    fm = FastMail(conf)

    background_tasks.add_task(fm.send_message, message, template_name="email.html")

    return {"message": "Email has been sent"}
