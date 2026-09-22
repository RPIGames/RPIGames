import uuid
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from .default.random_username import random_username


class Lobby(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    max_size: int
    secret: Optional[str] = Field(default=None)

    users: list["User"] = Relationship(back_populates="lobby")


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    secret: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str = Field(default_factory=random_username)
    leader: bool = Field(default=False)

    lobby_id: Optional[uuid.UUID] = Field(default=None, foreign_key="lobby.id")
    lobby: Optional[Lobby] = Relationship(back_populates="users")
