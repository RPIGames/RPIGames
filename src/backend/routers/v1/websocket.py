"""
This router file contains definitions for the /ws endpoints of the API.
"""

from json import JSONDecodeError
from typing import Literal, Callable
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ValidationError

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
    ServerConnectionStatusMessage,
    ClientRequestTimersMessage,
    ClientRequestScoreboardsMessage,
)
from games_api.player import Player
from games_api.lobby import get_players_lobby

router = APIRouter(
    prefix="/websocket",
    tags=["websocket"],
)


class ConnectionManager:
    """A Class to manage the websockets for all the different users."""

    def __init__(self):
        # active_connections is a dictionary from websockets to user ids.
        # if a WebSocket points to None, that means it's not authenticated yet
        self.active_connections: dict[WebSocket, UUID | None] = {}
        self.callable_map: dict[type[BaseModel], Callable] = {
            ClientAuthenticationMessage: self._authenticate,
            ClientRequestTimersMessage: self._request_timers,
            ClientRequestScoreboardsMessage: self._request_scoreboards,
            ClientSendChatMessage: self._send_chat_message,
            ClientSendLocationMessage: self._send_location,
            ClientSendButtonPressMessage: self._send_button_press,
            ClientFetchButtonArgumentsMessage: self._fetch_button_arguments,
        }

    async def handle(self, websocket: WebSocket, message: str):
        for model_type, function in self.callable_map.items():
            try:
                model = model_type.model_validate_json(message, strict=True)
            except ValidationError:
                continue
            await function(websocket, model)
            break

    ##############################################################################
    ########################### CONNECTION #######################################
    ##############################################################################

    async def _connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[websocket] = None
        await websocket.send_json(ServerConnectionStatusMessage(status="connection established"))

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
    ) -> None:
        if self._websocket_authenticated(websocket):
            return
        parsed_credentials = extract_credentials(credentials.token)
        if parsed_credentials is None:
            await websocket.send_json(ServerAuthenticationErrorMessage())
            return
        user = None
        # this has to be a for loop because get_session() is a generator.
        for session in get_session():
            user = optional_authorization(parsed_credentials, session)
        if user is None:
            await websocket.send_json(ServerAuthenticationErrorMessage())
            return
        self.active_connections[websocket] = user.uuid

    ##############################################################################
    ########################### TIMER ############################################
    ##############################################################################

    async def update_timers(
        self, player_id: UUID, timers: list[TimerData]
    ) -> None:
        model = ServerUpdateTimerMessage(data=timers)
        await self._send_model(player_id, model)

    async def delete_timers(self, player_id: UUID, timers: list[UUID]) -> None:
        model = ServerDeleteTimerMessage(ids=timers)
        await self._send_model(player_id, model)

    async def _request_timers(self, websocket: WebSocket, _) -> None:
        player_id = self._get_uuid(websocket)
        if player_id is None:
            return
        player = Player(player_id)
        timers = player._timer_request_all()
        model = ServerUpdateTimerMessage(data=timers)
        await websocket.send_json(model)

    ##############################################################################
    ########################### SCOREBOARD #######################################
    ##############################################################################

    async def update_scoreboards(
        self, player_id: UUID, scoreboards: list[ScoreboardData]
    ) -> None:
        model = ServerUpdateScoreboardMessage(data=scoreboards)
        await self._send_model(player_id, model)

    async def delete_scoreboards(
        self, player_id: UUID, scoreboards: list[UUID]
    ) -> None:
        model = ServerDeleteScoreboardMessage(ids=scoreboards)
        await self._send_model(player_id, model)

    async def _request_scoreboards(self, websocket: WebSocket, _) -> None:
        player_id = self._get_uuid(websocket)
        if player_id is None:
            return
        player = Player(player_id)
        lobby = get_players_lobby(player)
        if lobby is None:
            return
        scoreboards = lobby._game.scoreboard_get_all(player_id)
        model = ServerUpdateScoreboardMessage(data=scoreboards)
        await websocket.send_json(model)

    ##############################################################################
    ########################### CHAT #############################################
    ##############################################################################

    async def _send_chat_message(
        self, websocket: WebSocket, message: ClientSendChatMessage
    ) -> None:
        player_id = self._get_uuid(websocket)
        if player_id is None:
            return
        # TODO FOR NOW
        return

    async def send_message(self, room_id: UUID, message: str) -> None:
        # TODO this function
        pass

    async def update_chatrooms(
        self, player_id: UUID, chatrooms: list[ChatroomData]
    ) -> None:
        model = ServerNewChatroomPermissionsMessage(data=chatrooms)
        await self._send_model(player_id, model)

    ##############################################################################
    ########################### MAP ##############################################
    ##############################################################################

    async def update_markers(
        self, player_id: UUID, markers: list[MarkerData]
    ) -> None:
        model = ServerUpdateMarkerMessage(data=markers)
        await self._send_model(player_id, model)

    async def delete_markers(self, player_id: UUID, markers: list[UUID]) -> None:
        model = ServerDeleteMarkerMessage(ids=markers)
        await self._send_model(player_id, model)

    async def _send_location(
        self, websocket: WebSocket, location: ClientSendLocationMessage
    ) -> None:
        player_id = self._get_uuid(websocket)
        if player_id is None:
            return
        player = Player(player_id)
        player._set_location(location.location)

    ##############################################################################
    ########################### BUTTON ###########################################
    ##############################################################################

    async def _send_button_press(
        self, websocket: WebSocket, data: ClientSendButtonPressMessage
    ) -> None:
        player_id = self._get_uuid(websocket)
        if player_id is None:
            return
        # TODO this function
        return

    async def update_buttons(
        self, player_id: UUID, buttons: list[ButtonData]
    ) -> None:
        model = ServerUpdateButtonsMessage(data=buttons)
        await self._send_model(player_id, model)

    async def delete_buttons(self, player_id: UUID, buttons: list[UUID]) -> None:
        model = ServerDeleteButtonsMessage(ids=buttons)
        await self._send_model(player_id, model)

    async def _fetch_button_arguments(
        self, websocket: WebSocket, button: ClientFetchButtonArgumentsMessage
    ) -> None:
        player_id = self._get_uuid(websocket)
        if player_id is None:
            return
        # TODO this function
        return

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

    def _get_uuid(self, websocket: WebSocket) -> UUID | None:
        return self.active_connections.get(websocket, None)

manager = ConnectionManager()


@router.websocket("/")
async def websocket_endpoint(
    websocket: WebSocket,
):
    """This is the only WebSocket endpoint. All the code for managing the websockets should go in here."""
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
