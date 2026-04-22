import uuid
from sqlmodel import Field, SQLModel, Relationship

from .default.random_username import random_username

class Lobby(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    users: list[User] = Relationship(back_populates="lobby")


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(default_factory=random_username)
    leader: bool = Field(default=False)

    lobby_id: int | None = Field(default=None, foreign_key="lobby.id")
    lobby: Lobby = Relationship(back_populates="users")
