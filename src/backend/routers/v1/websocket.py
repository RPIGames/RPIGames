"""
This router file contains definitions for the /ws endpoints of the API.
"""

from json import JSONDecodeError
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from authentication.middleware import (
    extract_credentials,
    optional_authorization,
)
from db.engine import get_session
from models.websocket import (
    ButtonData,
    ChatroomData,
    ClientAuthenticationMessage,
    ClientFetchButtonArgumentsMessage,
    ClientSendButtonPressMessage,
    ClientSendChatMessage,
    ClientSendLocationMessage,
    MarkerData,
    ScoreboardData,
    ServerAuthenticationErrorMessage,
    ServerDeleteButtonsMessage,
    ServerDeleteMarkerMessage,
    ServerDeleteScoreboardMessage,
    ServerDeleteTimerMessage,
    ServerNewChatroomPermissionsMessage,
    ServerSendNotificationMessage,
    ServerUpdateButtonsMessage,
    ServerUpdateMarkerMessage,
    ServerUpdateScoreboardMessage,
    ServerUpdateTimerMessage,
    TimerData,
)

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
        self.callable_map = {}

    async def handle(self, websocket: WebSocket, message: str):
        pass

    ##############################################################################
    ########################### CONNECTION #######################################
    ##############################################################################

    async def _connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[websocket] = None

    def _disconnect(self, websocket: WebSocket):
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

    async def _authenticate(
        self, websocket: WebSocket, credentials: ClientAuthenticationMessage
    ) -> bool:
        if self._websocket_authenticated(websocket):
            return False
        parsed_credentials = extract_credentials(credentials.token)
        if parsed_credentials is None:
            await websocket.send_json(ServerAuthenticationErrorMessage())
            return False
        user = None
        # this has to be a for loop because get_session() is a generator.
        for session in get_session():
            user = optional_authorization(parsed_credentials, session)
        if user is None:
            await websocket.send_json(ServerAuthenticationErrorMessage())
            return False
        self.active_connections[websocket] = user.uuid
        return True

    ##############################################################################
    ########################### TIMER ############################################
    ##############################################################################

    async def update_timers(
        self, player_ids: list[UUID], timers: list[TimerData]
    ) -> None:
        model = ServerUpdateTimerMessage(data=timers)
        await self._broadcast_model(player_ids, model)

    async def delete_timers(self, player_ids: list[UUID], timers: list[UUID]) -> None:
        model = ServerDeleteTimerMessage(ids=timers)
        await self._broadcast_model(player_ids, model)

    async def _request_timers(self, websocket: WebSocket, _) -> None:
        if not self._websocket_authenticated(websocket):
            return
        timers = []
        # TODO ADD CODE TO GET THE DATA FOR THE MODELS HERE
        model = ServerUpdateTimerMessage(data=timers)
        await websocket.send_json(model)

    ##############################################################################
    ########################### SCOREBOARD #######################################
    ##############################################################################

    async def update_scoreboards(
        self, player_ids: list[UUID], scoreboards: list[ScoreboardData]
    ) -> None:
        model = ServerUpdateScoreboardMessage(data=scoreboards)
        await self._broadcast_model(player_ids, model)

    async def delete_scoreboards(
        self, player_ids: list[UUID], scoreboards: list[UUID]
    ) -> None:
        model = ServerDeleteScoreboardMessage(ids=scoreboards)
        await self._broadcast_model(player_ids, model)

    async def _request_scoreboards(self, websocket: WebSocket, _) -> None:
        scoreboards = []
        # TODO ADD CODE HERE
        model = ServerUpdateScoreboardMessage(data=scoreboards)
        await websocket.send_json(model)

    ##############################################################################
    ########################### CHAT #############################################
    ##############################################################################

    async def _send_chat_message(
        self, websocket: WebSocket, message: ClientSendChatMessage
    ) -> None:
        # TODO ADD CODE HERE
        pass

    async def send_message(self, room_id: UUID, message: str) -> None:
        # TODO this function
        pass

    async def update_chatrooms(
        self, player_ids: list[UUID], chatrooms: list[ChatroomData]
    ) -> None:
        model = ServerNewChatroomPermissionsMessage(data=chatrooms)
        await self._broadcast_model(player_ids, model)

    ##############################################################################
    ########################### MAP ##############################################
    ##############################################################################

    async def update_markers(
        self, player_ids: list[UUID], markers: list[MarkerData]
    ) -> None:
        model = ServerUpdateMarkerMessage(data=markers)
        await self._broadcast_model(player_ids, model)

    async def delete_markers(self, player_ids: list[UUID], markers: list[UUID]) -> None:
        model = ServerDeleteMarkerMessage(ids=markers)
        await self._broadcast_model(player_ids, model)

    async def _send_location(
        self, websocket: WebSocket, location: ClientSendLocationMessage
    ) -> None:
        # TODO this function
        pass

    ##############################################################################
    ########################### BUTTON ###########################################
    ##############################################################################

    async def _send_button_press(
        self, websocket: WebSocket, data: ClientSendButtonPressMessage
    ) -> None:
        # TODO this function
        pass

    async def update_buttons(
        self, player_ids: list[UUID], buttons: list[ButtonData]
    ) -> None:
        model = ServerUpdateButtonsMessage(data=buttons)
        await self._broadcast_model(player_ids, model)

    async def delete_buttons(self, player_ids: list[UUID], buttons: list[UUID]) -> None:
        model = ServerDeleteButtonsMessage(ids=buttons)
        await self._broadcast_model(player_ids, model)

    async def _fetch_button_arguments(
        self, websocket: WebSocket, button: ClientFetchButtonArgumentsMessage
    ) -> None:
        # TODO this function
        pass

    ##############################################################################
    ########################### NOTIFICATION #####################################
    ##############################################################################

    async def send_notification(
        self,
        player_id: UUID,
        text: str,
        native: bool,
        level: Literal["normal", "debug", "warning", "error"] = "normal",
    ) -> None:
        model = ServerSendNotificationMessage(level=level, native=native, text=text)
        await self._send_model(player_id, model)

    ##############################################################################
    ########################### HELPERS ##########################################
    ##############################################################################

    async def _broadcast_model(self, player_ids: list[UUID], model: BaseModel) -> None:
        for player_id in player_ids:
            await self._send_model(player_id, model)

    async def _send_model(self, player_id: UUID, model: BaseModel):
        sockets = self._get_websockets(player_id)
        for websocket in sockets:
            await websocket.send_json(model)

    def _get_websockets(self, player_id: UUID) -> list[WebSocket]:
        sockets = []
        for websocket, pid in self.active_connections.items():
            if pid == player_id:
                sockets.append(websocket)
        return sockets

    async def _broadcast(self, model: BaseModel):
        for websocket in self.active_connections:
            await websocket.send_json(model)


manager = ConnectionManager()


@router.websocket("/")
async def websocket_endpoint(
    websocket: WebSocket,
):
    """This is the only websocket endpoint. All the code for managing the websockets should go in here."""
    await manager._connect(websocket)
    try:
        while True:
            try:
                message = await websocket.receive_json()
                await manager.handle(websocket, message)
            except JSONDecodeError:
                pass

    except WebSocketDisconnect:
        manager._disconnect(websocket)
