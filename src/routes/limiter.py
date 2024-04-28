from fastapi import Depends, APIRouter
from fastapi_limiter.depends import RateLimiter

from src.entity.models import User
from src.schemas.user import UserResponse
from src.services.auth import auth_service


router = APIRouter(prefix="/limiter", tags=["limiter"])


@router.get(
    "/me",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    return user


