"""
Module for authentication settings in the FastAPI application.
"""

from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "default secret")
ALGORITHM = os.getenv("ALGORITHM")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
