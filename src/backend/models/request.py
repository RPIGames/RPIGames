"""
This module contains possible request models.
"""


from uuid import UUID

from pydantic import BaseModel


class LobbyJoinRequest(BaseModel):
    lobby_id: UUID
    lobby_secret: str | None = None

class MakeLobbyRequest(BaseModel):
    name: str | None = None
    secret: str | None = None

class LobbyPassLeadershipRequest(BaseModel):
    grantee_id: UUID
