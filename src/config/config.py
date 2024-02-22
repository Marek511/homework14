"""
Module defining settings for the FastAPI application.
"""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Settings class to configure the FastAPI application.

    Attributes:
        database_url (str): URL for the database connection.
        scheme (str): Scheme for the authentication.
        secret_key (str): Secret key for authentication.
        algorithm (str): Algorithm used for authentication.
        mail_username (str): Username for email configuration.
        mail_password (str): Password for email configuration.
        mail_from (str): Sender email address.
        mail_port (int): Port for email server.
        mail_server (str): Email server address.
        cloudinary_name (str): Cloudinary account name.
        cloudinary_api_key (str): API key for Cloudinary.
        cloudinary_api_secret (str): API secret for Cloudinary.
    """

    database_url: str
    scheme: str
    secret_key: str
    algorithm: str
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str


# Load settings from the specified .env file
settings = Settings(
    _env_file=Path(__file__).parent / ".env",
    _env_file_encoding="utf-8"
)
