"""
Module defining FastAPI endpoints for managing contacts.
"""

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from src.db.db import get_db
from src.db.models import Contact
from typing import Optional
from sqlalchemy.orm import Session

app = FastAPI()


class UserContact(BaseModel):
    """
    Pydantic model representing a user contact.
    """
    contact_id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birth_date: datetime
    additional_info: Optional[str] = None


@app.post("/contacts/")
def create_new_contact(contact: UserContact, session=Depends(get_db)):
    """
    Endpoint to create a new contact.

    Args:
        contact (UserContact): Pydantic model representing the contact details.
        session (Session): SQLAlchemy session.

    Returns:
        UserContact: Created contact details.
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
    return contact


@app.get("/contacts/")
def get_all_contacts_list(session: Session = Depends(get_db)):
    """
    Endpoint to get a list of all contacts.

    Args:
        session (Session): SQLAlchemy session.

    Returns:
        List[Contact]: List of all contacts.
    """
    contacts = session.query(Contact).all()
    return contacts


@app.get("/contacts/{contact_id}")
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to get details of a specific contact.

    Args:
        contact_id (int): Contact ID.
        db (Session): SQLAlchemy session.

    Returns:
        Contact: Details of the specified contact.
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@app.put("/contacts/{contact_id}")
def update_contact(
    contact_id: int,
    updated_contact: UserContact,
    session: Session = Depends(get_db)
):
    """
    Endpoint to update details of a specific contact.

    Args:
        contact_id (int): Contact ID.
        updated_contact (UserContact): Updated contact details.
        session (Session): SQLAlchemy session.

    Returns:
        dict: Success message.
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


@app.delete("/contacts/{contact_id}")
def delete_contact(
        contact_id: int,
        session: Session = Depends(get_db)
):
    """
    Endpoint to delete a specific contact.

    Args:
        contact_id (int): Contact ID.
        session (Session): SQLAlchemy session.

    Returns:
        dict: Success message.
    """
    db_contact = session.query(Contact).get(contact_id)

    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    session.delete(db_contact)
    session.commit()

    return {"message": "Success!"}
