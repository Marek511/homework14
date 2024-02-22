"""
Module defining SQLAlchemy models for Contact and User.
"""

from sqlalchemy import Column, Integer, String, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Contact(Base):
    """
    SQLAlchemy model for the 'contacts' table.
    """
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, index=True)
    birth_date = Column(Date)
    additional_data = Column(String, nullable=True)


class User(Base):
    """
    SQLAlchemy model for the 'users' table.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False)
    avatar = Column(String(255), nullable=True)
