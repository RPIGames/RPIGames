"""
This module contains dependencies used in endpoints to simplify authorization
and session cookies.

Authorization is done with a Bearer token that consists of two UUIDs (separated
by a '$'):

- The first is the user_token, a public uuid that anyone can use to look up public
  info on that user.
- The second is the secret_token, a private uuid that the server uses to verify that
  the person sending the request is who they say they are.
"""

from typing import Annotated, Optional
from uuid import UUID
from cryptography.hazmat.primitives import constant_time

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from db.models import User
from db.engine import get_session

security_optional = HTTPBearer(auto_error=False)

def is_logged_in (
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security_optional)],
) -> bool:
    """
    This dependency returns if a user sent a parsable Bearer token.
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

def optional_authorization (
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security_optional)],
    session: Annotated[Session, Depends(get_session)],
) -> Optional[User]:
    """
    This dependency allows the user to authenticate themselves, as
    long as the user passes a Bearer auth with the respective details.

    It returns the User object corresponding to that authentication,
    or None if the authentication failed or was non-existent
    """
    if credentials is None:
        return None

    if not credentials.scheme == "Bearer":
        return None

    credentials_list = credentials.credentials.split("$")

    if len(credentials_list) != 2:
        return None
    try:
        user_uuid = UUID(credentials_list[0])
        secret_uuid = UUID(credentials_list[1])
    except ValueError:
        return None

    user = session.get(User, user_uuid)

    if user == None:
        return None

    # constant time comparison of the UUIDs
    if not constant_time.bytes_eq(user.secret.bytes, secret_uuid.bytes):
        return None

    return user

def force_authorization (
    possible_auth: Annotated[Optional[User], Depends(optional_authorization)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    """
    This dependency forces the user to have a valid, active, user session,
    and that the user passes a Bearer auth with the respective details.

    It returns the User object corresponding to that authentication.
    """
    if possible_auth is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing, badly formatted, invalid, or expired authentication.")

    return possible_auth
