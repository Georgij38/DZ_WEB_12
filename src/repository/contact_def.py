
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from src.entity.models import Contact, User
from src.schemas.contact_schema import ContactCreate, ContactUpdate


async def get_birthdays_next_week(days: int, db: AsyncSession, user: User):
    """
    Retrieve contacts that have birthdays within the next specified number of days.

    This function selects contacts from the database that fall within the next week, based on the current date
    and the number of days specified. The birthdays are compared as strings in the format 'MM-DD'.

    Args:
        days (int): The number of days to look ahead for birthdays.
        db (AsyncSession): The database session.
        user (User): The user whose contacts are being retrieved.

    Returns:
        list[Contact]: A list of contacts that have birthdays within the next week.
    """

    current_date = datetime.now().date()
    next_week_date = current_date + timedelta(days=days)

    query = select(Contact).filter_by(user=user).where(
        func.to_char(Contact.birthday, 'MM-DD').between(
            current_date.strftime('%m-%d'),
            next_week_date.strftime('%m-%d')
        )
    )

    result = await db.execute(query)
    contacts = result.scalars().all()
    return contacts


async def create_contact(body: ContactCreate, db: AsyncSession, user: User):
    """
    Create a new contact and save it to the database.

    This function creates a new contact with the provided details and associates it with the specified user.
    The contact is then committed to the database.

    Args:
        body (ContactCreate): The details of the contact to create.
        db (AsyncSession): The database session.
        user (User): The user to associate with the new contact.

    Returns:
        Contact: The newly created contact.
    """
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    """
    Retrieve a list of contacts associated with the specified user.

    This function selects a limited number of contacts from the database, starting from an offset,
    and filters them by the specified user.

    Args:
        limit (int): The maximum number of contacts to retrieve.
        offset (int): The starting point for the retrieval.
        db (AsyncSession): The database session.
        user (User): The user whose contacts are being retrieved.

    Returns:
        list[Contact]: A list of contacts associated with the user.
    """
    result = await db.execute(select(Contact).filter_by(user=user).limit(limit).offset(offset))
    return result.scalars().all()


async def get_all_contacts(limit: int, offset: int, db: AsyncSession):
    """
    Retrieve a list of all contacts in the database.

    This function selects a limited number of contacts from the database, starting from an offset,
    without filtering by user.

    Args:
        limit (int): The maximum number of contacts to retrieve.
        offset (int): The starting point for the retrieval.
        db (AsyncSession): The database session.

    Returns:
        list[Contact]: A list of all contacts in the database.
    """

    result = await db.execute(select(Contact).limit(limit).offset(offset))
    return result.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    """
    Retrieve a contact by its ID associated with the specified user.

    This function selects a contact from the database by its ID and filters it by the specified user.

    Args:
        contact_id (int): The ID of the contact to retrieve.
        db (AsyncSession): The database session.
        user (User): The user whose contact is being retrieved.

    Returns:
        Contact: The contact with the specified ID, if it exists and is associated with the user.
                 Otherwise, returns None.
    """
    result = await db.execute(select(Contact).filter_by(user=user).where(Contact.id == contact_id))
    return result.scalar_one_or_none()


async def get_contact_query(query: str, db: AsyncSession, user: User):
    """
    Search for contacts based on a query string, associated with the specified user.

    This function selects contacts from the database that match the query string within
    the first name, last name, or email fields, and filters them by the specified user.

    Args:
        query (str): The search query string.
        db (AsyncSession): The database session.
        user (User): The user whose contacts are being searched.

    Returns:
        list[Contact]: A list of contacts that match the query and are associated with the user.
    """

    result = await db.execute(
        select(Contact).filter_by(user=user).where(
            (Contact.first_name.ilike(f'%{query}%')) |
            (Contact.last_name.ilike(f'%{query}%')) |
            (Contact.emails.ilike(f'%{query}%'))


        )
    )

    return result.scalars().all()


async def update_contact(contact_id: int, body: ContactUpdate, db: AsyncSession, user: User):
    """
    Update a contact by its ID associated with the specified user.

    This function retrieves a contact from the database by its ID and filters it by the specified user.
    It then updates the contact with the provided data and commits the changes to the database.

    Args:
        contact_id (int): The ID of the contact to update.
        body (ContactUpdate): The updated data for the contact.
        db (AsyncSession): The database session.
        user (User): The user whose contact is being updated.

    Returns:
        Contact: The updated contact, if it exists and is associated with the user.
                 Otherwise, returns None.
    """
    contact = await db.execute(select(Contact).filter_by(user=user).where(Contact.id == contact_id))
    contact = contact.scalars().first()

    if contact:
        update_data = body.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(contact, field, value)

        db.add(contact)
        await db.commit()
        await db.refresh(contact)

    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    """
    Delete a contact by its ID associated with the specified user.

    This function retrieves a contact from the database by its ID and filters it by the specified user.
    It then deletes the contact from the database.

    Args:
        contact_id (int): The ID of the contact to delete.
        db (AsyncSession): The database session.
        user (User): The user whose contact is being deleted.

    Returns:
        Contact: The deleted contact, if it exists and is associated with the user.
                 Otherwise, returns None.
    """
    contact = await get_contact(contact_id, db, user)
    if contact:
        await db.execute(delete(Contact).where(Contact.id == contact_id))
        await db.commit()
    return contact
