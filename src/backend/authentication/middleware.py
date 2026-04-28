from typing import Annotated, Optional
from uuid import UUID
from cryptography.hazmat.primitives import constant_time

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from db.models import User
from db.engine import get_session

security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)

# Dependecy, reads the Bearer token and returns the User model that it corresponds to
# Returns None if no authorization or if authorization failed
def is_logged_in (
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security_optional)],
) -> bool:
    """
    This dependency returns if a user sends a parsable Bearer token.
    """
    if credentials == None:
        return False
    if not credentials.scheme == "Bearer":
        return False
    if not "$" in credentials.credentials:
        return False
    credentials_list = credentials.credentials.split("$")
    if len(credentials_list) != 2:
        return False
    user_token = credentials_list[0]
    secret_token = credentials_list[1]
    if not len(user_token) == len(secret_token):
        return False
    return True

def force_authorization (
        credentials: HTTPAuthorizationCredentials = Depends(security),
        session: Session = Depends(get_session),
) -> User:
    """
    This dependency forces the user to have a valid, active, user session,
    and that the user passes a Bearer auth with the respective details.

    It returns the User object corresponding to that authentication.
    """
    if not credentials.scheme == "Bearer":
        raise HTTPException(status.HTTP_403_FORBIDDEN,
            {"detail": "Must have Bearer token."}
        )

    credentials_list = credentials.credentials.split("$")

    if len(credentials_list) != 2:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
            {"detail": "Badly formatted auth token."}
        )

    try:
        user_uuid = UUID(credentials_list[0])
        secret_uuid = UUID(credentials_list[1])
    except ValueError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
            {"detail": "Badly formed hexadecimal UUID String as auth token."}
        )

    user = session.get(User, user_uuid)

    if user == None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
            {"detail": "User token invalid or expired."}
        )

    # constant time comparison of the UUIDs
    if not constant_time.bytes_eq(user.secret.bytes, secret_uuid.bytes):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
            {"detail": "User token invalid or expired."}
        )

    return user
