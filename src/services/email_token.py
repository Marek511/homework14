"""
Module defining an EmailTokenManager class for handling email verification tokens.
"""

from datetime import datetime, timedelta
from fastapi import HTTPException
from jose import JWTError
from starlette import status
from src.routes import jwt


class EmailTokenManager:
    """
    Class for handling email verification tokens.

    Args:
        SECRET_KEY (str): Secret key used for token encoding and decoding.
        ALGORITHM (str): Algorithm used for token encoding and decoding.
    """
    def __init__(self, SECRET_KEY: str, ALGORITHM: str):
        self.SECRET_KEY = SECRET_KEY
        self.ALGORITHM = ALGORITHM

    def create_email_token(self, data: dict) -> str:
        """
        Create an email verification token.

        Args:
            data (dict): Data to be included in the token.

        Returns:
            str: Generated email verification token.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    def get_email_from_token(self, token: str) -> str:
        """
        Extract email from an email verification token.

        Args:
            token (str): Email verification token.

        Returns:
            str: Extracted email from the token.

        Raises:
            HTTPException: If the token is invalid or expired.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for email verification"
            )
