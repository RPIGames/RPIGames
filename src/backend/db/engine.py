import os
from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

try:
    sqlite_file_name = os.environ["DATABASE_PATH"]
except KeyError:
    sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)  # set parameter echo=true for debugging sql


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
