from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class ContactCreate(BaseModel):
    """
    Pydantic model for creating a contact.

    Attributes:
        first_name (str): The first name of the contact. Maximum length is 50 characters.
        last_name (str): The last name of the contact. Maximum length is 50 characters.
        birthday (Optional[date]): The birthday of the contact. Optional.
        emails (Optional[EmailStr]): The email address of the contact. Must be a valid email format. Optional.
        phone_numbers (Optional[str]): The phone number of the contact. Optional.
    """
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    birthday: Optional[date] = None
    emails: Optional[EmailStr] = None
    phone_numbers: Optional[str] = None


class ContactUpdate(BaseModel):
    """
    Pydantic model for updating a contact.

    Attributes:
        first_name (Optional[str]): The first name of the contact. Maximum length is 50 characters. Optional.
        last_name (Optional[str]): The last name of the contact. Maximum length is 50 characters. Optional.
        birthday (Optional[date]): The birthday of the contact. Optional.
        emails (Optional[EmailStr]): The email address of the contact. Must be a valid email format. Optional.
        phone_numbers (Optional[str]): The phone number of the contact. Optional.
    """
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    birthday: Optional[date] = None
    emails: Optional[EmailStr] = None
    phone_numbers: Optional[str] = None


class ContactsResponse(BaseModel):
    """
    Pydantic model for returning contact information.

    Attributes:
        id (int): The unique identifier of the contact.
        first_name (str): The first name of the contact.
        last_name (str): The last name of the contact.
        birthday (date): The birthday of the contact.
        emails (EmailStr): The email address of the contact.
        phone_numbers (str): The phone number of the contact.
        creation_date (Optional[date]): The date when the contact was created. Optional.
        last_update (Optional[date]): The date when the contact was last updated. Optional.
    """
    id: int
    first_name: str
    last_name: str
    birthday: date
    emails: EmailStr
    phone_numbers: str
    creation_date: Optional[date] = None
    last_update: Optional[date] = None

    class Config:
        from_attributes = True