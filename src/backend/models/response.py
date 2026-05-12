"""
This module contains possible response models.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel

class OkResponse(BaseModel):
    pass

class ErrorResponse(BaseModel):
    """Contains an error."""
    error: str

class AuthenticationErrorResponse(BaseModel):
    detail: Optional[str] = None

class LobbyResponse(BaseModel):
    id: UUID
    name: str
    max_members: int
    curr_members: int
    secret: Optional[str] = None

class UserTokenResponse(BaseModel):
    id: UUID
    secret: UUID

class PublicUserInfo(BaseModel):
    id: UUID
    name: str
    leader: bool = False
    lobby_id: Optional[UUID] = None

class PrivateUserInfo(PublicUserInfo):
    pass

class PublicUserInfoResponse(PublicUserInfo):
    pass

class PrivateUserInfoResponse(PrivateUserInfo):
    pass