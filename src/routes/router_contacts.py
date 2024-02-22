"""
Module defining API endpoints related to contacts with rate limiting and user authentication.
"""

from fastapi import Depends, APIRouter, Path, HTTPException, status
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter
from src.auth_files.auth_procedures import get_active_user
from src.db.db import get_db
from src.db.models import User
from src.schemas import ContactModel
from src.repository import contacts as repository_contacts

router = APIRouter(prefix='/contacts')


@router.post("/contacts/contacts/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def create_new_contact(
        contact: ContactModel,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_active_user)
):
    """
    Create a new contact.

    Args:
        contact (ContactModel): Contact data.
        db (Session, optional): SQLAlchemy session. Defaults to Depends(get_db).
        current_user (User, optional): Active user obtained from authentication. Defaults to Depends(get_active_user).

    Returns:
        dict: Created contact details.
    """
    return await repository_contacts.create_new_contact(contact, current_user, db)


@router.get("/contacts")
async def get_all_contact_list(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_active_user)
):
    """
    Get a list of all contacts for the current user.

    Args:
        db (Session, optional): SQLAlchemy session. Defaults to Depends(get_db).
        current_user (User, optional): Active user obtained from authentication. Defaults to Depends(get_active_user).

    Returns:
        List[dict]: List of contact details.
    """
    contacts = await repository_contacts.get_all_contacts_list(current_user, db)
    return contacts


@router.get("/contacts/{contact_id}")
async def get_contact(
        contact_id: int = Path(description="The ID of the contact to get", gt=0),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_active_user)
):
    """
    Get details of a specific contact for the current user.

    Args:
        contact_id (int): ID of the contact to retrieve.
        db (Session, optional): SQLAlchemy session. Defaults to Depends(get_db).
        current_user (User, optional): Active user obtained from authentication. Defaults to Depends(get_active_user).

    Returns:
        dict: Contact details.
    """
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.put("contacts//{contact_id}", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def update_contact(
        updated_contact: ContactModel,
        contact_id: int = Path(description="The ID of the contact to edit", gt=0),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_active_user)
):
    """
    Update details of a specific contact for the current user.

    Args:
        updated_contact (ContactModel): Updated contact data.
        contact_id (int): ID of the contact to update.
        db (Session, optional): SQLAlchemy session. Defaults to Depends(get_db).
        current_user (User, optional): Active user obtained from authentication. Defaults to Depends(get_active_user).

    Returns:
        dict: Updated contact details.
    """
    contact = await repository_contacts.update_contact(updated_contact, contact_id, current_user, db)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("contacts/{contact_id}", dependencies=[Depends(RateLimiter(times=2, seconds=30))])
async def delete_contact(
        contact_id: int = Path(description="The ID of the contact to delete", gt=0),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_active_user)
):
    """
    Delete a specific contact for the current user.

    Args:
        contact_id (int): ID of the contact to delete.
        db (Session, optional): SQLAlchemy session. Defaults to Depends(get_db).
        current_user (User, optional): Active user obtained from authentication. Defaults to Depends(get_active_user).

    Returns:
        dict: Details of the deleted contact.
    """
    contact = await repository_contacts.delete_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact
