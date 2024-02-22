"""
Module defining API endpoints related to user contacts with FastAPI.
"""
from typing import Optional
from fastapi import Depends, HTTPException, APIRouter, Query, FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from starlette import status
from src.db.db import get_db
from src.db.models import Contact, User
from src.auth_files.auth_procedures import get_active_user

app = FastAPI()

router = APIRouter(prefix='/contacts')

app.include_router(router)


class UserContact(BaseModel):
    contact_id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birth_date: datetime
    additional_info: Optional[str] = None


class UserUser(BaseModel):
    user_id: int
    email: str
    password: str
    refresh_token: str
    is_verified: bool = False
    avatar_url: Optional[str] = None


@router.post("/contacts/")
def create_new_contact(contact: UserContact, session: Session = Depends(get_db),
                       current_user: User = Depends(get_active_user)):
    """
    Create a new contact.

    Args:
        contact (UserContact): Contact data.
        session (Session, optional): SQLAlchemy session. Defaults to Depends(get_db).
        current_user (User, optional): Active user obtained from authentication. Defaults to Depends(get_active_user).

    Returns:
        dict: Response message and status code.
    """
    try:
        session.add(
            Contact(
                id=contact.contact_id,
                first_name=contact.first_name,
                last_name=contact.last_name,
                email=contact.email,
                phone_number=contact.phone_number,
                birth_date=contact.birth_date,
                additional_data=contact.additional_info
            )
        )
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

    return {"message": "Contact created successfully!", "status_code": status.HTTP_201_CREATED}


@router.get("/contacts/")
def get_all_contacts_list(session: Session = Depends(get_db), current_user: User = Depends(get_active_user)):
    """
    Get a list of all contacts.

    Args:
        session (Session, optional): SQLAlchemy session. Defaults to Depends(get_db).
        current_user (User, optional): Active user obtained from authentication. Defaults to Depends(get_active_user).

    Returns:
        List[Contact]: List of contacts.
    """
    contacts = session.query(Contact).all()
    return contacts


@router.get("/contacts/{contact_id}")
def get_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_active_user)):
    """
    Get details of a specific contact.

    Args:
        contact_id (int): ID of the contact to retrieve.
        db (Session, optional): SQLAlchemy session. Defaults to Depends(get_db).
        current_user (User, optional): Active user obtained from authentication. Defaults to Depends(get_active_user).

    Returns:
        Contact: Details of the contact.
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.put("/contacts/{contact_id}")
def update_contact(
    contact_id: int,
    updated_contact: UserContact,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_active_user)
):
    """
    Update details of a specific contact.

    Args:
        contact_id (int): ID of the contact to update.
        updated_contact (UserContact): Updated contact data.
        session (Session, optional): SQLAlchemy session. Defaults to Depends(get_db).
        current_user (User, optional): Active user obtained from authentication. Defaults to Depends(get_active_user).

    Returns:
        dict: Response message.
    """
    try:
        db_contact = session.query(Contact).get(contact_id)

        if db_contact is None:
            raise HTTPException(status_code=404, detail="Contact not found")

        db_contact.first_name = updated_contact.first_name
        db_contact.last_name = updated_contact.last_name
        db_contact.email = updated_contact.email
        db_contact.phone_number = updated_contact.phone_number
        db_contact.birth_date = updated_contact.birth_date
        db_contact.additional_data = updated_contact.additional_info

        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

    return {"message": "Success!"}


@router.delete("/contacts/{contact_id}")
def delete_contact(
        contact_id: int,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_active_user)
):
    """
    Delete a specific contact.

    Args:
        contact_id (int): ID of the contact to delete.
        session (Session, optional): SQLAlchemy session. Defaults to Depends(get_db).
        current_user (User, optional): Active user obtained from authentication. Defaults to Depends(get_active_user).

    Returns:
        dict: Response message and status code.
    """
    db_contact = session.query(Contact).get(contact_id)

    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    session.delete(db_contact)
    session.commit()

    return {"message": "Success!", "status_code": status.HTTP_204_NO_CONTENT}


@router.get("/contacts/")
def get_specific_contacts_list(session: Session = Depends(get_db), search: str = Query(None),
                               current_user: User = Depends(get_active_user)):
    """
    Get a list of contacts with optional search criteria.

    Args:
        session (Session, optional): SQLAlchemy session. Defaults to Depends(get_db).
        search (str, optional): Search term for filtering contacts. Defaults to None.
        current_user (User, optional): Active user obtained from authentication. Defaults to Depends(get_active_user).

    Returns:
        List[Contact]: List of contacts matching the search criteria.
    """
    if search:
        contacts = session.query(Contact).filter(
            (Contact.first_name.ilike(f"%{search}%")) |
            (Contact.last_name.ilike(f"%{search}%")) |
            (Contact.email.ilike(f"%{search}%"))
        ).all()
    else:
        contacts = session.query(Contact).all()
    return contacts


@router.get("/contacts/birthdays/")
def get_upcoming_birthdays(session: Session = Depends(get_db), current_user: User = Depends(get_active_user)):
    """
    Get a list of upcoming birthdays within the next 7 days.

    Args:
        session (Session, optional): SQLAlchemy session. Defaults to Depends(get_db).
        current_user (User, optional): Active user obtained from authentication. Defaults to Depends(get_active_user).

    Returns:
        List[Contact]: List of contacts with upcoming birthdays.
    """
    today = datetime.today()
    end_date = today + timedelta(days=7)

    upcoming_birthdays = session.query(Contact).filter(
        (Contact.birth_date >= today) & (Contact.birth_date <= end_date)
    ).all()

    return upcoming_birthdays
