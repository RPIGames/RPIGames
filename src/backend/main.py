from fastapi import Depends, FastAPI
from sqlmodel import Session, select

from db.models import Lobby
from db.engine import create_db_and_tables, get_session

from routers import user

create_db_and_tables()

app = FastAPI()

app.include_router(user.router)

@app.get("/get-lobbies")
def get_lobbies(
        session: Session = Depends(get_session),
    ):
    statement = select(Lobby)
    lobbies = session.exec(statement).all()
    return lobbies

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
