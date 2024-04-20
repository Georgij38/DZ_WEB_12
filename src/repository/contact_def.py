
from sqlalchemy import select, delete, func, exists
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from src.entity.models import Contact, User
from src.schemas.contact_schema import ContactCreate, ContactUpdate


async def get_birthdays_next_week(days: int, db: AsyncSession, user: User):

    current_date = datetime.now().date()
    next_week_date = current_date + timedelta(days=days)

    # Вибираємо контакти, які мають дні народження в наступні 7 днів
    query = select(Contact).filter_by(user=user).where(
        func.to_char(Contact.birthday, 'MM-DD').between(
            current_date.strftime('%m-%d'),
            next_week_date.strftime('%m-%d')
        )
    )

    # Виконуємо запит до бази даних
    result = await db.execute(query)
    contacts = result.scalars().all()
    return contacts


async def create_contact(body: ContactCreate, db: AsyncSession, user: User):
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    result = await db.execute(select(Contact).filter_by(user=user).limit(limit).offset(offset))
    return result.scalars().all()


async def get_all_contacts(limit: int, offset: int, db: AsyncSession):
    result = await db.execute(select(Contact).limit(limit).offset(offset))
    return result.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    result = await db.execute(select(Contact).filter_by(user=user).where(Contact.id == contact_id))
    return result.scalar_one_or_none()

async def get_contact_query(query: str, db: AsyncSession, user: User):

    result = await db.execute(
        select(Contact).filter_by(user=user).where(
            (Contact.first_name.ilike(f'%{query}%')) |
            (Contact.last_name.ilike(f'%{query}%')) |
            (Contact.emails.ilike(f'%{query}%'))


        )
    )

    return result.scalars().all()


async def update_contact(contact_id: int, body: ContactUpdate, db: AsyncSession, user: User):
    # Отримуємо контакт за його ID
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
    contact = await get_contact(contact_id, db, user)
    if contact:
        await db.execute(delete(Contact).where(Contact.id == contact_id))
        await db.commit()
    return contact
