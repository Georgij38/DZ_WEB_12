from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.repository import contact_def as repositories_contact
from src.schemas.contact_schema import ContactsResponse, ContactCreate, ContactUpdate
from src.entity.models import User, Role
from src.services.auth import auth_service
from src.services.roles import RoleAccess
from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix='/contacts', tags=['contacts'])
access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.get("/search/{query}", response_model=List[ContactsResponse], dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_contact_query(query: str, db: AsyncSession = Depends(get_db),
                            user: User = Depends(auth_service.get_current_user)):
    """
        Retrieve contacts based on a search query.

        Args:
            query (str): The search query.
            db (AsyncSession): The database session.
            user (User): The authenticated user.

        Returns:
            List[ContactsResponse]: A list of contacts that match the query.

        Raises:
            HTTPException: If no contacts are found for the query.
        """
    contact = await repositories_contact.get_contact_query(query, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact



@router.get("/birthdays", response_model=List[ContactsResponse], dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_birthdays_next_week(days: int = Query(7), db: AsyncSession = Depends(get_db),
                                  user: User = Depends(auth_service.get_current_user)):
    """
        Retrieve contacts with birthdays within the next week.

        Args:
            days (int): The number of days to consider for upcoming birthdays.
            db (AsyncSession): The database session.
            user (User): The authenticated user.

        Returns:
            List[ContactsResponse]: A list of contacts with birthdays within the next week.

        Raises:
            HTTPException: If no contacts are found with birthdays within the next week.
        """
    contact = await repositories_contact.get_birthdays_next_week(days, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.get("/", response_model=List[ContactsResponse], dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                           db: AsyncSession = Depends(get_db),
                           user: User = Depends(auth_service.get_current_user)):
    """
       Retrieve a list of contacts with pagination.

       Args:
           limit (int): The maximum number of contacts to return.
           offset (int): The starting index for the list of contacts.
           db (AsyncSession): The database session.
           user (User): The authenticated user.

       Returns:
           List[ContactsResponse]: A list of contacts.
       """
    contacts = await repositories_contact.get_contacts(limit, offset, db, user)
    return contacts


@router.get("/all", response_model=List[ContactsResponse],
            dependencies=[Depends(access_to_route_all), Depends(RateLimiter(times=1, seconds=20))])
async def get_all_contacts(limit: int = Query(10, ge=10, le=500),
                           offset: int = Query(0, ge=0),
                           db: AsyncSession = Depends(get_db)):
    """
        Retrieve all contacts with pagination, accessible only to admins and moderators.

        Args:
            limit (int): The maximum number of contacts to return.
            offset (int): The starting index for the list of contacts.
            db (AsyncSession): The database session.

        Returns:
            List[ContactsResponse]: A list of all contacts.
        """
    contacts = await repositories_contact.get_all_contacts(limit, offset, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactsResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    """
        Retrieve a single contact by its ID.

        Args:
            contact_id (int): The ID of the contact to retrieve.
            db (AsyncSession): The database session.
            user (User): The authenticated user.

        Returns:
            ContactsResponse: The contact with the given ID.

        Raises:
            HTTPException: If the contact is not found.
        """
    contact = await repositories_contact.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.post("/", response_model=ContactsResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def create_contact(body: ContactCreate, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
        Create a new contact.

        Args:
            body (ContactCreate): The data for the new contact.
            db (AsyncSession): The database session.
            user (User): The authenticated user.

        Returns:
            ContactsResponse: The newly created contact.
        """
    contact = await repositories_contact.create_contact(body, db, user)
    return contact


@router.put("/{contact_id}", response_model=ContactsResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def update_contact(body: ContactUpdate, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
        Update an existing contact.

        Args:
            body (ContactUpdate): The updated data for the contact.
            contact_id (int): The ID of the contact to update.
            db (AsyncSession): The database session.
            user (User): The authenticated user.

        Returns:
            ContactsResponse: The updated contact.

        Raises:
            HTTPException: If the contact is not found.
        """
    contact = await repositories_contact.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    Delete a contact by its ID.

    This function handles the deletion of a contact from the database. It requires authentication
    and ensures that the contact to be deleted exists. If the contact is not found, an HTTP 404
    response is returned.

    Args:
        contact_id (int): The ID of the contact to be deleted. It must be greater than or equal to 1.
        db (AsyncSession): The database session. This is obtained from the get_db dependency.
        user (User): The user who is currently logged in. This is obtained from the auth_service.get_current_user
                     dependency.

    Raises:
        HTTPException: If the contact with the given ID is not found. The response will have a status
                       code of 404 and a detail message of "NOT FOUND".

    Returns:
        None: If the contact is successfully deleted, no content is returned with a status code of 204.
    """
    contact = await repositories_contact.delete_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return None
