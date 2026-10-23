import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

### Base classes

class ClientMessage(BaseModel):
    pass

class ServerMessage(BaseModel):
    pass

class ServerErrorMessage(ServerMessage):
    type: Literal["error"] = "error"

### Data structs

class TimerData(BaseModel):
    """A class to store the timer data"""
    id: str
    name: str
    time: datetime.datetime

class ScoreboardData(BaseModel):
    """A class to store the scoreboard data"""
    id: str
    name: str
    sortable: bool
    headers: list[str]
    rows: list[list[str]]

class LocationData(BaseModel):
    """A class to store the location data"""
    accuracy: float
    latitude: float
    longitude: float
    altitude: float | None
    altitude_accuracy: float | None
    heading: float | None
    speed: float | None
    time: datetime.datetime

class MarkerData(BaseModel):
    """A class to store a marker's data"""
    id: str
    name: str
    latitude: float
    longitude: float

class ButtonData(BaseModel):
    """A class to store a button's data"""
    id: UUID
    name: str
    needs_arguments: bool

### Authentication flow messages

class ServerStatusMessage(ServerMessage):
    """A Response to send to the user when the status of the connection changed. """
    type: Literal["status"] = "status"
    status: Literal["connection established", "authenticated"]

class ClientAuthenticationMessage(ClientMessage):
    """The user sends a token with this format with the authentication credentials"""
    type: Literal["authentication"]
    token: str

class ServerAuthenticationErrorMessage(ServerErrorMessage):
    """A Response to send to the user when there was an error authenticating"""
    type: Literal["error"] = "error"
    status: Literal["authentication_failed"] = "authentication_failed"

### Server update timer messages

class ServerTimerMessage(ServerMessage):
    """A base class all timer server messages are derived from"""
    type: Literal["timer"] = "timer"

class ServerUpdateTimerMessage(ServerTimerMessage):
    """A Response to send to the user when a timer is updated or a new one created."""
    action: Literal["update"] = "update"
    data: TimerData

class ServerDeleteTimerMessage(ServerTimerMessage):
    """A Response to send to the user when a timer is deleted"""
    action: Literal["delete"] = "delete"
    id: UUID

class ClientRequestMessage(ClientMessage):
    """A model for when the user wants all the timers data"""
    type: Literal["timer", "scoreboard"]
    action: Literal["request_all"]

class ServerRecieveAllTimerMessage(ServerTimerMessage):
    """A Response to send to the user when all the timers are requested"""
    action: Literal["recieve_all"] = "recieve_all"
    data: list[TimerData]

### Scoreboard messages

class ServerScoreboardMessage(ServerMessage):
    """A base class for all scoreboard server messages"""
    type: Literal["scoreboard"] = "scoreboard"

class ServerUpdateScoreboardMessage(ServerScoreboardMessage):
    """A Response to send to the user when a scoreboard is updated or a new
    scoreboard is created."""
    action: Literal["update"] = "update"
    data: ScoreboardData

class ServerDeleteScoreboardMessage(ServerScoreboardMessage):
    """A Response to send to the user when a scoreboard is deleted"""
    action: Literal["delete"] = "delete"
    id: UUID

class ServerRecieveAllScoreboardMessage(ServerScoreboardMessage):
    """A Response to send to the user when all the scoreboard data is requested"""
    action: Literal["recieve_all"] = "recieve_all"
    data: list[ScoreboardData]

### Chat messages

class ClientSendChatMessage(ClientMessage):
    """A model for when the user sends a message"""
    type: Literal["chat"]
    message: str
    room_id: str

class ServerChatErrorMessage(ServerErrorMessage):
    """A Response to send to the user after they send a message, if there's an error"""
    type: Literal["error"] = "error"
    category: Literal["chat"] = "chat"
    message: Literal["no chat room", "bad message"]

class ServerChatMessage(ServerMessage):
    """A base response to send to a user when an event about char happens"""
    type: Literal["chat"] = "chat"

class ServerRecieveChatMessage(ServerChatMessage):
    """A Response to send to the user when they receive a message"""
    room_id: str
    author_id: UUID | Literal["-1"] = "-1"
    message: str

class ServerNewChatroomPermissionsMessage(ServerChatMessage):
    """
    A response to sent to the user when a chatroom they are in changes permissions
    or they have access to a new chatroom.
    """
    room_id: str
    read: bool
    write: bool

### Map messages

class ServerMarkerMessage(ServerMessage):
    """A base response to send to a user when a map message needs to be sent"""
    type: Literal["map"] = "map"

class ServerUpdateMarkerMessage(ServerMarkerMessage):
    """A Response to send to the user when a marker is updated or a new one created."""
    action: Literal["update_marker"] = "update_marker"
    data: MarkerData

class ServerDeleteMarkerMessage(ServerMarkerMessage):
    """A Response to send to the user when a marker is deleted"""
    action: Literal["delete_marker"] = "delete_marker"
    id: str

class ClientSendLocationMessage(ClientMessage):
    """A model for when the user sends their location"""
    type: Literal["map"] = "map"
    location: LocationData

## Button messages

class ClientSendButtonPressMessage(ClientMessage):
    """A model for when the user sends a button"""
    type: Literal["button"] = "button"
    id: str
    args: list[str] | None

class ServerButtonMessage(ServerMessage):
    """A base response to send to a user from the server when a button
    message needs to be sent"""
    type: Literal["button"] = "button"

class ServerUpdateButtonMessage(ServerButtonMessage):
    """A Response to send to the user when a button is updated or a new one created."""
    action: Literal["update"] = "update"
    data: ButtonData

class ServerDeleteButtonMessage(ServerButtonMessage):
    """A Response to send to the user when a button is deleted."""
    action: Literal["delete"] = "delete"
    id: str

class ClientFetchButtonArgumentsMessage(ClientMessage):
    """
    A message sent from the client to the server when they clicked on a button
    and wish to know what parameters to select from.
    """
    type: Literal["button"]
    action: Literal["get_params"]
    id: str # button id

class ServerSendButtonArgumentsMessage(ServerButtonMessage):
    """A message sent from the server to supply the parameter options for a user"""
    action: Literal["params"] = "params"
    id: str
    params: list[list[str]]

### Notifications

class ServerSendNotificationMessage(ServerMessage):
    """A message sent from the server to notify the user's device"""
    type: Literal["notification"] = "notification"
    level: Literal["normal", "debug", "warning", "error"] = "normal"
    native: bool
    text: str
