
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.database.db import get_db
from src.repository import users as repository_users
from src.conf.config import config


class Auth:
    """
    Authentication service for handling user authentication and token management.

    Attributes:
        pwd_context (CryptContext): Password hashing context using bcrypt.
        SECRET_KEY (str): Secret key for JWT encoding and decoding.
        ALGORITHM (str): Algorithm used for JWT encoding and decoding.
        oauth2_scheme (OAuth2PasswordBearer): OAuth2 password bearer scheme for token authentication.

    Methods:
        verify_password(plain_password, hashed_password):
            Verifies a plain password against a hashed password.

        get_password_hash(password):
            Hashes a password using bcrypt.

        create_access_token(data, expires_delta=None):
            Creates an access token with the provided data and expiration time.

        create_refresh_token(data, expires_delta=None):
            Creates a refresh token with the provided data and expiration time.

        decode_refresh_token(refresh_token):
            Decodes a refresh token and returns the email if the token is valid.

        get_current_user(token, db):
            Retrieves the current user based on the provided token and database session.

        create_email_token(data):
            Creates an email verification token with the provided data.

        get_email_from_token(token):
            Decodes an email verification token and returns the email if the token is valid.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = config.SECRET_KEY_JWT
    ALGORITHM = config.ALGORITHM

    def verify_password(self, plain_password, hashed_password):
        """
        Verifies a plain password against a hashed password.

        Args:
            plain_password (str): The plain password to verify.
            hashed_password (str): The hashed password to compare against.

        Returns:
            bool: True if the passwords match, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Hashes a password using bcrypt.

        Args:
            password (str): The password to hash.

        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Create a new access token.

        This method generates a JSON Web Token (JWT) with the provided data and an expiration time.
        The token is signed with the secret key and the specified algorithm.

        Args:
            data (dict): The data to be encoded in the JWT.
            expires_delta (Optional[float]): The number of seconds until the token expires. If not provided,
                                             the token will expire after 15 minutes.

        Returns:
            str: The encoded JWT access token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Create a new refresh token.

        This method generates a JSON Web Token (JWT) with the provided data and an expiration time.
        The token is signed with the secret key and the specified algorithm.

        Args:
            data (dict): The data to be encoded in the JWT.
            expires_delta (Optional[float]): The number of seconds until the token expires. If not provided,
                                             the token will expire after 7 days.

        Returns:
            str: The encoded JWT refresh token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=7)
        to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        Decode a refresh token and return the email if the token is valid and has the correct scope.

        Args:
            refresh_token (str): The refresh token to decode.

        Raises:
            HTTPException: If the token is invalid or has an incorrect scope.

        Returns:
            str: The email associated with the refresh token.
        """

        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
        """
        Retrieve the current user based on the provided token and database session.

        Args:
            token (str): The access token to validate.
            db (AsyncSession): The database session.

        Raises:
            HTTPException: If the token is invalid, has an incorrect scope, or the user does not exist.

        Returns:
            User: The user associated with the token.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user

    def create_email_token(self, data: dict):
        """
        Create an email verification token.

        Args:
            data (dict): The data to encode in the token.

        Returns:
            str: The encoded email verification token.
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=1)
        to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
        Decode an email verification token and return the email if the token is valid.

        Args:
            token (str): The email verification token to decode.

        Raises:
            HTTPException: If the token is invalid.

        Returns:
            str: The email associated with the token.
        """

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")


auth_service = Auth()
