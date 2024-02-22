"""
Module for database operations in the FastAPI application.
"""

from databases import Database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base

DATABASE_URL = "sqlite:///./my_contacts_for_users_db.sqlite"


database = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Initialize the database by creating all tables defined in the models.

    :return: None
    """
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Get a database session.

    :return: Database session
    :rtype: sqlalchemy.orm.Session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
