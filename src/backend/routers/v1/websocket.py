"""
This router file contains definitions for the /ws endpoints of the API.
"""

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
    ClientRequestScoreboardsMessage, ServerReceiveChatMessage,
)
from games_api.player import Player
from games_api.lobby import get_players_lobby, GLOBAL_LOBBY_MAP

router = APIRouter(
    prefix="/websocket",
    tags=["websocket"],
)


class ConnectionManager:
    """A Class to manage the websockets for all the different users."""

    def __new__(cls, *args, **kwargs):
        raise TypeError(f"{cls.__name__} is a static class and cannot be instantiated.")

    @classmethod
    async def handle(cls, websocket: WebSocket, message: str):
        for model_type, function in cls.callable_map.items():
            try:
                model = model_type.model_validate_json(message, strict=True)
            except ValidationError:
                continue
            await function(websocket, model)
            break

    ##############################################################################
    ########################### CONNECTION #######################################
    ##############################################################################

    @classmethod
    async def _connect(cls, websocket: WebSocket):
        await websocket.accept()
        cls.active_connections[websocket] = None
        await websocket.send_json(ServerConnectionStatusMessage(status="connection established"))

    @classmethod
    def _disconnect(cls, websocket: WebSocket):
        cls.active_connections.pop(websocket, None)

    ##############################################################################
    ########################### AUTHENTICATION ###################################
    ##############################################################################

    @classmethod
    def authenticated(cls, player_id: UUID) -> bool:
        for websocket, pid in cls.active_connections.items():
            if pid == player_id:
                return cls._websocket_authenticated(websocket)
        return False

    @classmethod
    def _websocket_authenticated(cls, websocket: WebSocket):
        return cls.active_connections.get(websocket, None) is not None

    @classmethod
    async def _authenticate(
        cls, websocket: WebSocket, credentials: ClientAuthenticationMessage
    ) -> None:
        if cls._websocket_authenticated(websocket):
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
        cls.active_connections[websocket] = user.uuid
        await websocket.send_json(ServerConnectionStatusMessage(status="authenticated"))

    ##############################################################################
    ########################### TIMER ############################################
    ##############################################################################

    @classmethod
    async def update_timers(
        cls, player_id: UUID, timers: list[TimerData]
    ) -> None:
        if not timers:
            return
        model = ServerUpdateTimerMessage(data=timers)
        await cls._send_model(player_id, model)

    @classmethod
    async def delete_timers(cls, player_id: UUID, timers: list[UUID]) -> None:
        if not timers:
            return
        model = ServerDeleteTimerMessage(ids=timers)
        await cls._send_model(player_id, model)

    @classmethod
    async def _request_timers(cls, websocket: WebSocket, _) -> None:
        player_id = cls._get_uuid(websocket)
        if player_id is None:
            return
        player = Player(player_id)
        timers = player._timer_request_all()
        model = ServerUpdateTimerMessage(data=timers)
        await websocket.send_json(model)

    ##############################################################################
    ########################### SCOREBOARD #######################################
    ##############################################################################

    @classmethod
    async def update_scoreboards(
        cls, player_id: UUID, scoreboards: list[ScoreboardData]
    ) -> None:
        if not scoreboards:
            return
        model = ServerUpdateScoreboardMessage(data=scoreboards)
        await cls._send_model(player_id, model)

    @classmethod
    async def delete_scoreboards(
        cls, player_id: UUID, scoreboards: list[UUID]
    ) -> None:
        if not scoreboards:
            return
        model = ServerDeleteScoreboardMessage(ids=scoreboards)
        await cls._send_model(player_id, model)

    @classmethod
    async def _request_scoreboards(cls, websocket: WebSocket, _) -> None:
        player_id = cls._get_uuid(websocket)
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

    @classmethod
    async def _send_chat_message(
        cls, websocket: WebSocket, message: ClientSendChatMessage
    ) -> None:
        player_id = cls._get_uuid(websocket)
        if player_id is None:
            return
        player = Player(player_id)
        lobby = get_players_lobby(player)
        if lobby is None:
            return
        game = lobby._game
        author_id, room_id, message = game.parse_message(player_id, message.room_id, message.message)
        await cls.send_message(lobby._uuid, author_id, room_id, message)

    @classmethod
    async def send_message(cls, lobby_id: UUID, author_id: UUID, room_id: UUID, message: str) -> None:
        lobby = GLOBAL_LOBBY_MAP.get(lobby_id, None)
        if lobby is None:
            return
        player_ids = lobby._game.get_room(room_id)
        model = ServerReceiveChatMessage(room_id=room_id, author_id=author_id, message=message)
        for player_id in player_ids:
            await cls._send_model(player_id, model)

    @classmethod
    async def update_chatrooms(
        cls, player_id: UUID, chatrooms: list[ChatroomData]
    ) -> None:
        if not chatrooms:
            return
        model = ServerNewChatroomPermissionsMessage(data=chatrooms)
        await cls._send_model(player_id, model)

    @classmethod
    async def delete_chatroom(cls, player_id: UUID, chatrooms: list[ChatroomData]) -> None:
	if not chatrooms:
	    return
	model = ServerDeleteChatroomMessage(ids=chatrooms)
	await cls._send_model(player_id, model)

    ##############################################################################
    ########################### MAP ##############################################
    ##############################################################################

    @classmethod
    async def update_markers(
        cls, player_id: UUID, markers: list[MarkerData]
    ) -> None:
        if not markers:
            return
        model = ServerUpdateMarkerMessage(data=markers)
        await cls._send_model(player_id, model)

    @classmethod
    async def delete_markers(cls, player_id: UUID, markers: list[UUID]) -> None:
        if not markers:
            return
        model = ServerDeleteMarkerMessage(ids=markers)
        await cls._send_model(player_id, model)

    @classmethod
    async def _send_location(
        cls, websocket: WebSocket, location: ClientSendLocationMessage
    ) -> None:
        player_id = cls._get_uuid(websocket)
        if player_id is None:
            return
        player = Player(player_id)
        player._set_location(location.location)

    ##############################################################################
    ########################### BUTTON ###########################################
    ##############################################################################

    @classmethod
    async def _send_button_press(
        cls, websocket: WebSocket, data: ClientSendButtonPressMessage
    ) -> None:
        raise NotImplementedError()

    @classmethod
    async def update_buttons(
        cls, player_id: UUID, buttons: list[ButtonData]
    ) -> None:
        if not buttons:
            return
        model = ServerUpdateButtonsMessage(data=buttons)
        await cls._send_model(player_id, model)

    @classmethod
    async def delete_buttons(cls, player_id: UUID, buttons: list[UUID]) -> None:
        if not buttons:
            return
        model = ServerDeleteButtonsMessage(ids=buttons)
        await cls._send_model(player_id, model)

    @classmethod
    async def _fetch_button_arguments(
        cls, websocket: WebSocket, button: ClientFetchButtonArgumentsMessage
    ) -> None:
        raise NotImplementedError()

    ##############################################################################
    ########################### NOTIFICATION #####################################
    ##############################################################################

    @classmethod
    async def send_notification(
        cls,
        player_id: UUID,
        text: str,
        native: bool,
        level: Literal["normal", "debug", "warning", "error"] = "normal",
    ) -> None:
        model = ServerSendNotificationMessage(level=level, native=native, text=text)
        await cls._send_model(player_id, model)

    ##############################################################################
    ########################### HELPERS ##########################################
    ##############################################################################

    @classmethod
    async def _send_model(cls, player_id: UUID, model: BaseModel):
        sockets = cls._get_websockets(player_id)
        for websocket in sockets:
            await websocket.send_json(model)

    @classmethod
    def _get_websockets(cls, player_id: UUID) -> list[WebSocket]:
        sockets = []
        for websocket, pid in cls.active_connections.items():
            if pid == player_id:
                sockets.append(websocket)
        return sockets

    @classmethod
    def _get_uuid(cls, websocket: WebSocket) -> UUID | None:
        return cls.active_connections.get(websocket, None)

    ##############################################################################
    ########################### CLASS VARIABLES ##################################
    ##############################################################################

    active_connections: dict[WebSocket, UUID | None] = {}

    callable_map: dict[type[BaseModel], Callable] = {
        ClientAuthenticationMessage: _authenticate,
        ClientRequestTimersMessage: _request_timers,
        ClientRequestScoreboardsMessage: _request_scoreboards,
        ClientSendChatMessage: _send_chat_message,
        ClientSendLocationMessage: _send_location,
        ClientSendButtonPressMessage: _send_button_press,
        ClientFetchButtonArgumentsMessage: _fetch_button_arguments,
    }

@router.websocket("/")
async def websocket_endpoint(
    websocket: WebSocket,
):
    """This is the only WebSocket endpoint. All the code for managing the websockets should go in here."""
    await ConnectionManager._connect(websocket)
    try:
        while True:
            message = await websocket.receive_json()
            await ConnectionManager.handle(websocket, message)
    except WebSocketDisconnect:
        ConnectionManager._disconnect(websocket)
