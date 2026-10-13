from uuid import UUID
from typing import Any, Literal
import datetime

from pydantic import BaseModel

class TimerData(BaseModel):
    """A class to store the timer data"""
    id: UUID
    name: str
    time: datetime.datetime

class ScoreboardData(BaseModel):
    """A class to store the scoreboard data"""
    id: UUID
    name: str
    sortable: bool
    headers: list[str]
    rows: list[list[str]]

class LocationData(BaseModel):
    """A class to store the location data"""
    accuracy: float | None
    latitude: float | None
    longitude: float | None
    altitude: float | None
    altitude_accuracy: float | None
    heading: float | None
    speed: float | None

class MarkerData(BaseModel):
    """A class to store the marker data"""
    id: UUID
    name: str
    location: LocationData

class ButtonData:
    """A class to store the button data"""
    id: UUID
    name: str
    arguments: list[list[str]]

class HandshakeConnectionEstablishedResponseModel(BaseModel):
    """A Response to send to the user when the connection is established. Contains the phrase "connection established". """
    type: str = "status"
    status: str = "connection established"

class HandshakeAuthenticationTokenModel(BaseModel):
    """The user sends a token with this format with the authentication credentials"""
    type: str = "authentication"
    token: str

class HandshakeAuthenticationResponseModel(BaseModel):
    """A Response to send to the user when the authentication is successful"""
    type: str = "status"
    status: Literal["authenticated", "authentication_failed"]

class TimerUpdateResponseModel(BaseModel):
    """A Response to send to the user when a timer is updated or a new one created."""
    type: str = "timer"
    action: str = "update"
    data: TimerData

class TimerDeleteResponseModel(BaseModel):
    """A Response to send to the user when a timer is deleted"""
    type: str = "timer"
    action: str = "delete"
    id: UUID

class TimerRequestAllModel(BaseModel):
    """A model for when the user wants all the timers data"""
    type: str = "timer"
    action: str = "request_all"

class TimerRequestAllResponseModel(BaseModel):
    """A Response to send to the user when all the timers are requested"""
    type: str = "timer"
    action: str = "receive_all"
    data: list[TimerData]

class ScoreboardUpdateResponseModel(BaseModel):
    """A Response to send to the user when a scoreboard is updated or a new scoreboard is created."""
    type: str = "scoreboard"
    action: str = "update"
    data: ScoreboardData

class ScoreboardDeleteResponseModel(BaseModel):
    """A Response to send to the user when a scoreboard is deleted"""
    type: str = "scoreboard"
    action: str = "delete"
    id: UUID

class ScoreboardRequestAllModel(BaseModel):
    """A model for when the user wants all the scoreboard data"""
    type: str = "scoreboard"
    action: str = "request_all"

class ScoreboardRequestAllResponseModel(BaseModel):
    """A Response to send to the user when all the scoreboard data is requested"""
    type: str = "scoreboard"
    action: str = "receive_all"
    data: list[ScoreboardData]

class ChatSendMessageModel(BaseModel):
    """A model for when the user sends a message"""
    type: str = "chat"
    message: str
    room_id: UUID

class ChatSendMessageErrorResponseModel(BaseModel):
    """A Response to send to the user after they send a message, if there's an error"""
    type: str = "error"
    category: str = "chat"
    message: Literal["no chat room", "bad message"]

class ChatReceiveMessageResponseModel(BaseModel):
    """A Response to send to the user when they receive a message"""
    type: str = "chat"
    room_id: UUID
    author_id: UUID | -1
    message: str

class MapSendLocationModel(BaseModel):
    """A model for when the user sends their location"""
    type: str = "map"
    location: LocationData

class MapUpdateMarkerResponseModel(BaseModel):
    """A Response to send to the user when a marker is updated or a new one created."""
    type: str = "map"
    action: str = "update_marker"
    data: MarkerData

class MapDeleteMarkerResponseModel(BaseModel):
    """A Response to send to the user when a marker is deleted"""
    type: str = "map"
    action: str = "delete_marker"
    id: UUID

class ButtonSendModel(BaseModel):
    """A model for when the user sends a button"""
    type: str = "button"
    id: UUID
    args: list[Any]

class ButtonUpdateResponseModel(BaseModel):
    """A Response to send to the user when a button is updated or a new one created."""
    type: str = "button"
    action: str = "update"
    data: ButtonData

