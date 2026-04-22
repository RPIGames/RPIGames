from fastapi import FastAPI
from sqlmodel import Session, select

from db.engine import engine, create_db_and_tables

from db.models import User, Lobby

create_db_and_tables(engine)

app = FastAPI()

@app.get("/get-lobbies")
def get_lobbies():
    with Session(engine) as session:
        statement = select(Lobby)
        lobbies = session.exec(statement).all()
    return lobbies


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
