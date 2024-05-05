from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import users as repositories_users
from src.schemas.user import UserSchema, TokenSchema, UserResponse, RequestEmail
from src.services.auth import auth_service
from src.services.email import send_email
from src.conf import messages
router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, bt: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    """
    The signup function creates a new user in the database.
        It takes in a UserSchema object, which is validated by pydantic.
        If the email already exists, it raises an HTTPException with status code 409 (Conflict).
        Otherwise, it hashes the password and creates a new user using create_user from repositories/users.py.

    :param body: UserSchema: Validate the request body
    :param bt: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the application
    :param db: AsyncSession: Get the database session
    :return: A user object
    :doc-author: Trelent
    """
    exist_user = await repositories_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=messages.ACCOUNT_EXIST)
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repositories_users.create_user(body, db)
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login", response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
        Handle user login.

        This endpoint allows users to log in using their email and password. It verifies the credentials,
        generates access and refresh tokens, and updates the user's refresh token in the database.

        Args:
            body (OAuth2PasswordRequestForm): The login credentials.
            db (AsyncSession): The database session.

        Raises:
            HTTPException: If the email is invalid, the email is not confirmed, or the password is invalid,
                           with appropriate status codes and error messages.

        Returns:
            dict: A dictionary containing the access token, refresh token, and token type.
        """
    user = await repositories_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenSchema)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
                        db: AsyncSession = Depends(get_db)):
    """
       Refresh the access token.

       This endpoint allows users to refresh their access token using their refresh token. It verifies
       the refresh token, generates new access and refresh tokens, and updates the user's refresh token
       in the database.

       Args:
           credentials (HTTPAuthorizationCredentials): The credentials containing the refresh token.
           db (AsyncSession): The database session.

       Raises:
           HTTPException: If the refresh token is invalid, with a 401 status code and a message indicating
                          that the refresh token is invalid.

       Returns:
           dict: A dictionary containing the new access token, refresh token, and token type.
       """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repositories_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
        Confirm a user's email.

        This endpoint allows users to confirm their email address by providing a token. It verifies the
        token, checks if the user exists, and if the email is not already confirmed, it confirms the email.

        Args:
            token (str): The confirmation token.
            db (AsyncSession): The database session.

        Raises:
            HTTPException: If the verification fails, with a 400 status code and a message indicating
                           that there was a verification error.

        Returns:
            dict: A dictionary containing a message indicating whether the email is already confirmed
                  or if the confirmation was successful.
        """
    email = await auth_service.get_email_from_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repositories_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    """
        Request email confirmation.

        This endpoint allows users to request an email confirmation. It checks if the user's email is
        already confirmed and if not, it adds a task to send a confirmation email to the background tasks.

        Args:
            body (RequestEmail): The request body containing the user's email.
            background_tasks (BackgroundTasks): The background tasks manager.
            request (Request): The HTTP request object.
            db (AsyncSession): The database session.

        Returns:
            dict: A dictionary containing a message indicating whether the email is already confirmed
                  or to check the email for confirmation.
        """
    user = await repositories_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}
