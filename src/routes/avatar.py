import pickle

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserResponse
from src.services.auth import auth_service
from src.conf.config import config
from src.repository import users as repositories_users

router = APIRouter(prefix="/avatar", tags=["avatar"])
cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True,
)


@router.patch(
    "/avatar",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_current_user(
    file: UploadFile = File(),
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
        Update the avatar of the current user.

        This function handles the upload of a new avatar image for the user, updates the avatar URL in the database,
        and updates the user's information in the cache. The avatar is resized to 250x250 pixels and cropped to fill the
        given dimensions.

        Args:
            file (UploadFile, optional): The file to be uploaded as the new avatar. Defaults to File().
            user (User): The user who is currently logged in. This is obtained from the auth_service.get_current_user
                         dependency.
            db (AsyncSession): The database session. This is obtained from the get_db dependency.

        Returns:
            UserResponse: The updated user information.
    """
    public_id = f"Avatar/{user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
    print(res)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    user = await repositories_users.update_avatar_url(user.email, res_url, db)
    auth_service.cache.set(user.email, pickle.dumps(user))
    auth_service.cache.expire(user.email, 300)
    return user
