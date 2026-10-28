import uuid

from sqlmodel import Field, SQLModel

from .default.random_username import random_username


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    secret: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str = Field(default_factory=random_username)
