from fastapi import Depends, FastAPI
from sqlmodel import Session, select

from db.models import Lobby
from db.engine import create_db_and_tables, get_session

from routers import user

create_db_and_tables()

app = FastAPI(
    root_path="/api"
)

app.include_router(user.router)

