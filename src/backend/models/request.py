"""
This module contains possible request models.
"""

from uuid import UUID

from pydantic import BaseModel


class LobbyJoinRequest(BaseModel):
    lobby_id: UUID
    lobby_secret: str | None = None


class MakeLobbyRequest(BaseModel):
    game_type_id: str
    game_capacity: int
    game_config: dict[str, str | int | float | bool]
    name: str | None = None
    secret: str | None = None


class LobbyPassLeadershipRequest(BaseModel):
    grantee_id: UUID
