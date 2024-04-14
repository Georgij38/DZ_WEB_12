from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

# Схема для створення нового контакту
class ContactCreate(BaseModel):
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    birthday: Optional[date] = None
    emails: Optional[EmailStr] = None
    phone_numbers: Optional[str] = None

# Схема для оновлення моделі Contact
class ContactUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    birthday: Optional[date] = None
    emails: Optional[EmailStr] = None
    phone_numbers: Optional[str] = None

# Схема для повернення списку контактів
class ContactsResponse(BaseModel):
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