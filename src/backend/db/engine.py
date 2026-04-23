import os

from sqlmodel import create_engine, SQLModel

from .models import Lobby, User

try:
    sqlite_file_name = os.environ["DATABASE_PATH"]
except KeyError:
    sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables(engine):
    SQLModel.metadata.create_all(engine)
