import os
from typing import Generator

from sqlmodel import create_engine, Session, SQLModel


try:
    sqlite_file_name = os.environ["DATABASE_PATH"]
except KeyError:
    sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
