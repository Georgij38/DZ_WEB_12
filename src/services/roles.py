from fastapi import Request, Depends, HTTPException, status

from src.entity.models import Role, User
from src.services.auth import auth_service


class RoleAccess:
    """
    A class to manage access control based on user roles.

    This class is designed to be used as a dependency in FastAPI endpoints to restrict access to certain roles.

    Attributes:
        allowed_roles (list[Role]): A list of roles that are allowed to access the endpoint.

    Methods:
        __call__(request: Request, user: User = Depends(auth_service.get_current_user)):
            This method is called when the class instance is used as a dependency. It checks if the user's role
            is in the list of allowed roles. If the user's role is not allowed, it raises an HTTPException with
            a 403 status code.
    """
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, user: User = Depends(auth_service.get_current_user)):
        """
        Check if the user's role is allowed to access the endpoint.

        This method is called when the class instance is used as a dependency. It checks if the user's role
        is in the list of allowed roles. If the user's role is not allowed, it raises an HTTPException with
        a 403 status code.

        Args:
            request (Request): The incoming request.
            user (User): The user object retrieved from the JWT token in the request. This is obtained by
                         calling the `get_current_user` method from the `auth_service`.

        Raises:
            HTTPException: If the user's role is not in the list of allowed roles.
        """
        print(user.role, self.allowed_roles)
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="FORBIDDEN"
            )
