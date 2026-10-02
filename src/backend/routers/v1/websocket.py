"""
This router file contains definitions for the /ws endpoints of the API.
"""
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from authentication.middleware import extract_credentials, optional_authorization
from db.engine import get_session

router = APIRouter(
    prefix="/websocket",
    tags=["websocket"],
)

class ConnectionManager:
    """A Class to manage the websockets for all the different users."""
    def __init__(self):
        self.active_connections: dict[WebSocket, UUID | None] = dict()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[websocket] = None

    def disconnect(self, websocket: WebSocket):
        self.active_connections.pop(websocket, None)

    def authenticated(self, websocket: WebSocket) -> bool:
        return self.active_connections.get(websocket, None) is not None

    def authenticate(self, credentials: str, websocket: WebSocket) -> bool:
        if self.authenticated(websocket):
            return True
        credentials = extract_credentials(credentials.split(' ')[1])
        user = None
        # this has to be a for loop because get_session() is a generator (which it has to be to close the session).
        for session in get_session():
            user = optional_authorization(credentials, session)
        if user is None:
            return False
        self.active_connections[websocket] = user.id
        return True

    @staticmethod
    async def send_personal_message(message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@router.websocket("/")
async def websocket_endpoint(
        websocket: WebSocket,
        ):
    """This is the only websocket endpoint. All the code for managing the websockets should go in here."""
    await manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            if not manager.authenticated(websocket):
                if manager.authenticate(message, websocket):
                    await manager.send_personal_message("Authentication Successful", websocket)
                else:
                    await manager.send_personal_message("We fed your credentials to THE SNAKE.", websocket)
            else:
                await manager.send_personal_message(message, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

