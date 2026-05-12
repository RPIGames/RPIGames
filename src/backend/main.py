from fastapi import FastAPI

from db.engine import create_db_and_tables

from routers.v1_router import router as router_v1

create_db_and_tables()

app = FastAPI(
    root_path="/api"
)

app.include_router(router_v1, prefix="/v1")

app.include_router(router_v1, prefix="/latest")

