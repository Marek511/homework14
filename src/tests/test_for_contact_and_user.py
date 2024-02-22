import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base, Contact, User
from datetime import date


@pytest.fixture
def engine():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


def test_contact_model(session):
    contact_data = {
        "first_name": "Mark",
        "last_name": "K",
        "email": "mark.k@example.com",
        "phone_number": "123-456-789",
        "birth_date": date(1999, 1, 1),
        "additional_data": "Some additional data"
    }
    contact = Contact(**contact_data)

    session.add(contact)
    session.commit()

    retrieved_contact = session.query(Contact).filter_by(email=contact_data["email"]).first()
    assert retrieved_contact is not None
    assert retrieved_contact.first_name == contact_data["first_name"]
    assert retrieved_contact.last_name == contact_data["last_name"]
    assert retrieved_contact.phone_number == contact_data["phone_number"]
    assert retrieved_contact.birth_date == contact_data["birth_date"]
    assert retrieved_contact.additional_data == contact_data["additional_data"]


def test_user_model(session):
    user_data = {
        "email": "testuser@example.com",
        "password": "secret",
        "refresh_token": "refresh_token123",
        "is_verified": True,
        "avatar": "avatar.jpg"
    }
    user = User(**user_data)

    session.add(user)
    session.commit()

    retrieved_user = session.query(User).filter_by(email=user_data["email"]).first()
    assert retrieved_user is not None
    assert retrieved_user.password == user_data["password"]
    assert retrieved_user.refresh_token == user_data["refresh_token"]
    assert retrieved_user.is_verified == user_data["is_verified"]
    assert retrieved_user.avatar == user_data["avatar"]
