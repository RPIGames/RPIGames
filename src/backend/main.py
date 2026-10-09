from fastapi import FastAPI

from db.engine import create_db_and_tables
from routers.v1_router import router as router_v1

create_db_and_tables()

description = """
This is the backend documentation for this project. It shows the schema of the api and can be used for testing. 

## User
* **/user/new** - Get new User token
* **/user/info_self** - Get User info
* **/user/info** - Get public info 
* **/user/change_name** - Changes the users name
* **/user/sign_out** - signs the user out

## Lobby
* **/lobby/all** - get all the lobbies
* **/lobby/new** - make a lobby
* **/lobby/join** - join a lobby
* **/lobby/leave** - leaves a lobby
* **/lobby/leadership/grant**  - grant leadership by current leader

"""
app = FastAPI(
    title = "RPIGames",
    root_path="/api",
    description = description,
    version = "0.1.0",
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/license/mit",
    },
    )

app.include_router(router_v1, prefix="/v1", include_in_schema=False)

app.include_router(router_v1, prefix="/latest")
