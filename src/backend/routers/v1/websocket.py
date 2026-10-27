"""
This router file contains definitions for the /ws endpoints of the API.
"""
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from authentication.middleware import extract_credentials, optional_authorization
from db.engine import get_session
from models.websocket import ClientAuthenticationMessage, ServerAuthenticationErrorMessage

router = APIRouter(
    prefix="/websocket",
    tags=["websocket"],
)

class ConnectionManager:
    """A Class to manage the websockets for all the different users."""
    def __init__(self):
        # active_connections is a dictionary from websockets to user ids.
        # if a websocket points to None, that means it's not authenticated yet
        self.active_connections: dict[WebSocket, UUID | None] = {}
        self.callable_map = {

        }

    async def handle(self, message: str):
        pass

    ##############################################################################
    ########################### CONNECTION #######################################
    ##############################################################################

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[websocket] = None

    def disconnect(self, websocket: WebSocket):
        self.active_connections.pop(websocket, None)

    ##############################################################################
    ########################### AUTHENTICATION ###################################
    ##############################################################################

    def authenticated(self, player_id: UUID) -> bool:
        for websocket, pid in self.active_connections.items():
            if pid == player_id:
                return self._websocket_authenticated(websocket)
        return False

    def _websocket_authenticated(self, websocket: WebSocket):
        return self.active_connections.get(websocket, None) is not None

    async def _authenticate(self, websocket: WebSocket, credentials: ClientAuthenticationMessage) -> None:
        if self._websocket_authenticated(websocket):
            return
        user = None
        # this has to be a for loop because get_session() is a generator (which it has to be to close the session).
        for session in get_session():
            user = optional_authorization(credentials.token, session)
        if user is None:
            pass

    ##############################################################################
    ########################### TIMER ############################################
    ##############################################################################

    ##############################################################################
    ########################### SCOREBOARD #######################################
    ##############################################################################

    ##############################################################################
    ########################### CHAT #############################################
    ##############################################################################

    ##############################################################################
    ########################### MAP ##############################################
    ##############################################################################

    ##############################################################################
    ########################### BUTTON ###########################################
    ##############################################################################

    ##############################################################################
    ########################### NOTIFICATION #####################################
    ##############################################################################

    ##############################################################################
    ########################### HELPERS ##########################################
    ##############################################################################

    async def _send_personal_message(self, player_id: UUID, message: str):
        for websocket, pid in self.active_connections.items():
            if pid == player_id:
                await self._send_websocket_message(websocket, message)

    @staticmethod
    async def _send_websocket_message(websocket: WebSocket, message: str):
        await websocket.send_json(message)

    async def _broadcast(self, message: str):
        for websocket, _ in self.active_connections.items():
            await websocket.send_json(message)

manager = ConnectionManager()

@router.websocket("/")
async def websocket_endpoint(
        websocket: WebSocket,
        ):
    """This is the only websocket endpoint. All the code for managing the websockets should go in here."""
    await manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive_json()
            await manager.handle(message)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
