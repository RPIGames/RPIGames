import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

##############################################################################
########################### Base classes #####################################
##############################################################################

class ServerErrorMessage(BaseModel):
    type: Literal["error"] = "error"

##############################################################################
########################### Structs ##########################################
##############################################################################

class TimerData(BaseModel):
    """A class to store the timer data"""
    id: str
    name: str
    time: datetime.datetime
    disappear_on_completion: bool

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
    time: datetime.datetime
    altitude: float | None = None
    altitude_accuracy: float | None = None
    heading: float | None = None
    speed: float | None = None

class MarkerData(BaseModel):
    """A class to store a marker's data"""
    id: str
    name: str
    latitude: float
    longitude: float

class ChatroomPermissionsData(BaseModel):
    """A class that stores the permission data for a chatroom"""
    room_id: str
    read: bool
    write: bool

class ButtonData(BaseModel):
    """A class to store a button's data"""
    id: str
    name: str
    needs_arguments: bool

##############################################################################
########################### AUTHENTICATION ###################################
##############################################################################

class ServerConnectionStatusMessage(BaseModel):
    """A Response to send to the user when the status of the connection changed. """
    type: Literal["status"] = "status"
    status: Literal["connection established", "authenticated"]

class ClientAuthenticationMessage(BaseModel):
    """The user sends a token with this format with the authentication credentials"""
    type: Literal["authentication"]
    token: str

class ServerAuthenticationErrorMessage(ServerErrorMessage):
    """A Response to send to the user when there was an error authenticating"""
    category: Literal["authentication"] = "authentication"
    status: Literal["authentication failed"] = "authentication failed"

##############################################################################
########################### Timer ############################################
##############################################################################

class ServerTimerMessage(BaseModel):
    """A base class all timer server messages are derived from"""
    type: Literal["timer"] = "timer"

class ServerUpdateTimerMessage(ServerTimerMessage):
    """A Response to send to the user when a timer is updated or a new one created."""
    action: Literal["update"] = "update"
    data: list[TimerData]

class ServerDeleteTimerMessage(ServerTimerMessage):
    """A Response to send to the user when a timer is deleted"""
    action: Literal["delete"] = "delete"
    ids: list[str]

class ClientRequestTimersMessage(BaseModel):
    """A model for when the user wants all the timers data"""
    type: Literal["timer"]
    action: Literal["request_all"]

##############################################################################
########################### Scoreboard #######################################
##############################################################################

class ServerScoreboardMessage(BaseModel):
    """A base class for all scoreboard server messages"""
    type: Literal["scoreboard"] = "scoreboard"

class ServerUpdateScoreboardMessage(ServerScoreboardMessage):
    """A Response to send to the user when a scoreboard is updated or a new
    scoreboard is created."""
    action: Literal["update"] = "update"
    data: list[ScoreboardData]

class ServerDeleteScoreboardMessage(ServerScoreboardMessage):
    """A Response to send to the user when a scoreboard is deleted"""
    action: Literal["delete"] = "delete"
    ids: list[str]

class ClientRequestScoreboardsMessage(BaseModel):
    type: Literal["scoreboard"]
    action: Literal["request_all"]

##############################################################################
########################### Chat #############################################
##############################################################################

class ServerChatMessage(BaseModel):
    """A base class for all chat server messages"""
    type: Literal["chat"] = "chat"

class ClientSendChatMessage(BaseModel):
    """A model for when the user sends a message"""
    type: Literal["chat"]
    message: str
    room_id: str

class ServerChatErrorMessage(ServerErrorMessage):
    """A Response to send to the user after they send a message, if there's an error"""
    category: Literal["chat"] = "chat"
    message: Literal["no chat room", "bad message"]

class ServerReceiveChatMessage(ServerChatMessage):
    """A Response to send to the user when they receive a message"""
    room_id: str
    author_id: UUID | Literal["-1"] = "-1"
    message: str

class ServerNewChatroomPermissionsMessage(ServerChatMessage):
    """
    A response to sent to the user when a chatroom they are in changes permissions
    or they have access to a new chatroom.
    """
    data: list[ChatroomPermissionsData]

##############################################################################
########################### MAP ##############################################
##############################################################################

class ServerMarkerMessage(BaseModel):
    """A base response to send to a user when a map message needs to be sent"""
    type: Literal["map"] = "map"

class ServerUpdateMarkerMessage(ServerMarkerMessage):
    """A Response to send to the user when a marker is updated or a new one created."""
    action: Literal["update_marker"] = "update_marker"
    data: list[MarkerData]

class ServerDeleteMarkerMessage(ServerMarkerMessage):
    """A Response to send to the user when a marker is deleted"""
    action: Literal["delete_marker"] = "delete_marker"
    ids: list[str]

class ClientSendLocationMessage(BaseModel):
    """A model for when the user sends their location"""
    type: Literal["map"] = "map"
    location: LocationData

##############################################################################
########################### BUTTON ###########################################
##############################################################################

class ClientSendButtonPressMessage(BaseModel):
    """A model for when the user sends a button"""
    type: Literal["button"]
    id: str
    args: list[str] | None

class ServerButtonMessage(BaseModel):
    """A base response to send to a user from the server when a button
    message needs to be sent"""
    type: Literal["button"] = "button"

class ServerUpdateButtonsMessage(ServerButtonMessage):
    """A Response to send to the user when a button is updated or a new one created."""
    action: Literal["update"] = "update"
    data: list[ButtonData]

class ServerDeleteButtonMessage(ServerButtonMessage):
    """A Response to send to the user when a button is deleted."""
    action: Literal["delete"] = "delete"
    id: str

class ClientFetchButtonArgumentsMessage(BaseModel):
    """
    A message sent from the client to the server when they clicked on a button
    and wish to know what parameters to select from.
    """
    type: Literal["button"]
    id: str  # button id
    action: Literal["get_params"]

class ServerSendButtonArgumentsMessage(ServerButtonMessage):
    """A message sent from the server to supply the parameter options for a user"""
    action: Literal["params"] = "params"
    id: str
    params: list[list[str]]

##############################################################################
########################### NOTIFICATIONS ####################################
##############################################################################

class ServerSendNotificationMessage(BaseModel):
    """A message sent from the server to notify the user's device"""
    type: Literal["notification"] = "notification"
    level: Literal["normal", "debug", "warning", "error"] = "normal"
    native: bool
    text: str
