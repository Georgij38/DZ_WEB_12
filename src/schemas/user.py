from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from src.entity.models import Role


class UserSchema(BaseModel):
    """
   Pydantic model for user registration and login.

   Attributes:
       username (str): The username of the user. Minimum length is 3 characters, maximum length is 50 characters.
       email (EmailStr): The email address of the user. Must be a valid email format.
       password (str): The password of the user. Minimum length is 6 characters, maximum length is 8 characters.
   """
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=8)


class UserResponse(BaseModel):
    """
    Pydantic model for returning user information.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        email (EmailStr): The email address of the user.
        avatar (Optional[str]): The URL of the user's avatar image. Optional.
        role (Role): The role of the user, which is an instance of the `Role` model.
    """
    id: int = 1
    username: str
    email: EmailStr
    avatar: str | None
    role: Role

    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    """
    Pydantic model for returning access and refresh tokens.

    Attributes:
        access_token (str): The access token for authentication.
        refresh_token (str): The refresh token for token refresh.
        token_type (str): The type of the token, which is typically "bearer".
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    """
    Pydantic model for requesting email confirmation.

    Attributes:
        email (EmailStr): The email address to be confirmed. Must be a valid email format.
    """
    email: EmailStr
