"""
This file contains the Player sub-API for the Game API.
"""
import asyncio
from collections.abc import Callable
from datetime import datetime
from typing import Any, TypeVar
from uuid import UUID

from sqlmodel import Session

from db.engine import engine
from db.models import User
from games_api.schedule import schedule

T = TypeVar("T")

class Player:
    def __init__(self, uuid: UUID) -> None:
        self.uuid = uuid
        db_conn = Session(engine)
        user = db_conn.get(User, self.uuid)
        if user is None:
            raise ValueError
        self._user = user
        self._location = None
        self._timers : dict[str, tuple[str, str, datetime, Callable[[], None], bool ]] = {}

    def __eq__(self, value: object, /) -> bool:
        if type(value) == Player:
            return value.uuid == self.uuid
        return False

    #when websockets are implemented fix deal with right type of location
    async def _set_location(self, new_location: tuple[float, float]) -> None:
        """
        Sets the location of the player.
        """
        self._location = new_location

    def get_name(self) -> str:
        """
        Gets the name of this player.
        """
        return self._user.name

    #when websockets are implemented fix deal with right type of location
    def get_location(self) -> tuple[float, float] | None:
        """
        Gets the location of the current player. May return None if no location can be found
        """
        return self._location

    def assign_chatroom(
        self, chatroom_id: UUID, read_permission=True, send_permission=True
    ):
        """
        Assigns a chatroom to the player, so that the player can see it.
        """
        raise NotImplementedError("Chatrooms have not been implemented yet")

    def unassign_chatroom(self, chatroom_id: UUID):
        """
        Unassigns a chatroom to the player, so that the player stops seeing it.
        """
        raise NotImplementedError("Chatrooms have not been implemented yet")

    #Chat_Send_Message(Room UUID, message): this player has sent this message
    async def chat_send_message(
        self,
        Room_UUID:str|UUID,
        message:str
        ) -> None:
        pass

    def send_notification(
        self, notification_title: str, notification_body: str | None = None
    ):
        """
        Sends a notification to a player. This is implied to be a in-app notification, but may
        also be a push notification if permission is available.
        """
        raise NotImplementedError("Notifications have not been implemented yet")

    def make_timer(
        self,
        timer_id : str | UUID,
        timer_end: datetime,
        timer_name: str = "Untitled Timer",
        timer_end_function: Callable[[], None] | None = None,
        disappear_on_completion: bool = True,
    ) -> tuple[str, str, datetime, Callable[[], None], bool ]: #id , name  , time of end, function called at end,  disappear on completion
        """
        This makes the timer and adds it to the list of timers that the player sees 
        """
        if timer_end_function is None:
            timer_end_function = lambda : None
        if type(timer_id) is not str:
            assert type(timer_id) is UUID
            timer_id = timer_id.hex
        self._timers[timer_id] = (timer_id,timer_name,timer_end,timer_end_function,disappear_on_completion)
        amount_of_seconds = timer_end.timestamp() - (datetime.now()).timestamp()
        amount_of_seconds = amount_of_seconds/60
        schedule.schedule(amount_of_seconds,_check_timer,timer_id,timer_end_function)
        return (timer_id,timer_name,timer_end,timer_end_function,disappear_on_completion)

    # Timer_request_all(): this player has requested all timers
    async def _timer_request_all(self) -> dict[str, tuple[str,str, datetime,Callable[[], None], bool]]:
        return self._timers

    #stop timer
    async def stop_timer(self,
        timer_id : str | UUID):
        """
        Tries to remove the time if the timer does not exist return false otherwise return true
        """
        checking = self._timers.pop(timer_id,None)
        if(checking == None):
            return False
        else:
            return True



    #todo add function that is a helper function that when the function is called makes sure the called function is in the list of timers.
    # has atributes of fuction being called and timer id
    async def _check_timer(
        self,
        timer_id : str | UUID,
        timer_end_function: Callable[[], None] | None = None,
    )-> asyncio.Task[Any]:
        """
        Does the action that is to be called by the timer if the timer still exists.
        """
        if timer_id in _timer:
            return await timer_end_function()
        else:
            pass


    def assign_button(
        self,
        button_id: UUID | str,
        button_function: Callable[["Player", T], Any],
        button_name: str = "Unnamed Button",
        *,
        selection: None | list[T] = None,
    ) -> None:
        if isinstance(button_id, str):
            button_id = UUID(bytes=button_id.encode("ascii"))
        raise NotImplementedError("Buttons have not been implemented yet")

    async def button_send(
        self,
        Button_ID: str| UUID,
        arguments: list[str]
        )-> None:
         pass
        #: this player pushed this button
