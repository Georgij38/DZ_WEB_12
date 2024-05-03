from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserSchema


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a user by their email from the database.

    This function selects a user from the database by their email.

    Args:
        email (str): The email of the user to retrieve.
        db (AsyncSession): The database session.

    Returns:
        User: The user with the specified email, if it exists. Otherwise, returns None.
    """
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()

    return user


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    Create a new user and save it to the database.

    This function creates a new user with the provided details and saves it to the database.

    Args:
        body (UserSchema): The details of the user to create.
        db (AsyncSession): The database session.

    Returns:
        User: The newly created user.
    """
    new_user = User(**body.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
    Update the refresh token for a user in the database.

    This function updates the refresh token for a user and commits the changes to the database.

    Args:
        user (User): The user whose token is to be updated.
        token (str | None): The new refresh token.
        db (AsyncSession): The database session.
    """
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    Mark a user's email as confirmed in the database.

    This function retrieves a user by their email and marks their email as confirmed, then commits the changes to the database.

    Args:
        email (str): The email of the user to confirm.
        db (AsyncSession): The database session.
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    """
    Update the avatar URL for a user in the database.

    This function retrieves a user by their email, updates their avatar URL, commits the changes to the database,
    and refreshes the user object.

    Args:
        email (str): The email of the user whose avatar is to be updated.
        url (str | None): The new avatar URL.
        db (AsyncSession): The database session.

    Returns:
        User: The updated user.
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user
