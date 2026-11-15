import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from app.core.config import settings

security = HTTPBasic()


class AuthenticatedUser(BaseModel):
    username: str
    role: str  # "readonly" or "admin"


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)) -> AuthenticatedUser:
    """
    Validates HTTP Basic Auth credentials against configured read-only and admin credentials.
    Uses secrets.compare_digest to defend against timing attacks.
    """
    is_admin_user = secrets.compare_digest(credentials.username, settings.API_ADMIN_USERNAME)
    is_admin_pass = secrets.compare_digest(credentials.password, settings.API_ADMIN_PASSWORD)

    if is_admin_user and is_admin_pass:
        return AuthenticatedUser(username=credentials.username, role="admin")

    is_readonly_user = secrets.compare_digest(credentials.username, settings.API_READONLY_USERNAME)
    is_readonly_pass = secrets.compare_digest(credentials.password, settings.API_READONLY_PASSWORD)

    if is_readonly_user and is_readonly_pass:
        return AuthenticatedUser(username=credentials.username, role="readonly")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Basic"},
    )


def require_readonly_user(user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
    """Allows either read-only or admin users to access read endpoints."""
    return user


def require_admin_user(user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
    """Restricts access exclusively to admin users (e.g. for manual synchronization triggers)."""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Admin privileges required for this action"
        )
    return user

