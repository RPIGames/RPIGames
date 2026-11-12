"""
This file contains the Player sub-API for the Game API.
"""

from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any, TypeVar
from uuid import UUID

from sqlmodel import Session

from db.engine import engine
from db.models import User
from games_api.schedule import schedule
from models.websocket import LocationData,ChatroomData,TimerData

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
        self._timers: dict[
            UUID, tuple[TimerData, Callable[[], Awaitable[Any]] | None]
        ] = {}

    def __eq__(self, value: object, /) -> bool:
        if type(value) is Player:
            return value.uuid == self.uuid
        return False

    # when websockets are implemented fix deal with right type of location
    async def _set_location(self, new_location: LocationData) -> None:
        """
        Sets the location of the player.
        """
        self._location = new_location

    def get_name(self) -> str:
        """
        Gets the name of this player.
        """
        return self._user.name

    # when websockets are implemented fix deal with right type of location
    def get_location(self) -> LocationData | None:
        """
        Gets the location of the current player. May return None if no location can be found
        """
        return self._location

    def get_uuid()->UUID:
        return self.uuid

    def assign_chatroom(
        self, chatroom_id: UUID, read_permission=True, send_permission=True
    ):
        """
        Assigns a chatroom to the player, so that the player can see it.
        """
        raise NotImplementedError("Chatrooms have not been implemented yet")

    #get chatrooms in 

    def unassign_chatroom(self, chatroom_id: UUID):
        """
        Unassigns a chatroom to the player, so that the player stops seeing it.
        """
        raise NotImplementedError("Chatrooms have not been implemented yet")

    def send_notification(
        self,
        notification_title: str,
        notification_body: str | None = None,
        native: bool = False,
    ):
        """
        Sends a notification to a player. This is implied to be a in-app notification, but may
        also be a push notification if permission is available.
        """
        raise NotImplementedError("Notifications have not been implemented yet")

    def make_timer(
        self,
        timer_id: UUID,
        timer_end: datetime,
        timer_name: str = "Untitled Timer",
        timer_end_function: Callable[[], Awaitable[Any]] | None = None,
        disappear_on_completion: bool = True,
    ) -> tuple[
        TimerData, Callable[[], Awaitable[Any]] | None
    ]: 
        """
        This makes the timer and adds it to the list of timers that the player sees
        """
        
        self._timers[timer_id] = (
            timer_id,
            timer_name,
            timer_end,
            timer_end_function,
            disappear_on_completion,
        )
        amount_of_seconds = timer_end.timestamp() - (datetime.now()).timestamp()
        amount_of_seconds = amount_of_seconds / 60
        schedule(amount_of_seconds, self._check_timer, timer_id, timer_end_function)
        return (
            timer_id,
            timer_name,
            timer_end,
            timer_end_function,
            disappear_on_completion,
        )

    # Timer_request_all(): this player has requested all timers
    async def _timer_request_all(
        self,
    ) -> list[
        TimerData
    ]:
        timers_list = []
        for timer in self._timers:
            timer_list.append(timer[0])
        return timers_list

    # stop timer
    async def stop_timer(self, timer_id: UUID):
        """
        Tries to remove the time if the timer does not exist return false otherwise return true
        """
        checking = self._timers.pop(timer_id, None)
        return checking != None

    # todo add function that is a helper function that when the function is called makes sure the called function is in the list of timers.
    # has atributes of fuction being called and timer id
    async def _check_timer(
        self,
        timer_id: UUID,
        timer_end_function: Callable[[], Awaitable[Any]] | None = None,
    ):
        """
        Does the action that is to be called by the timer if the timer still exists.
        """
        if timer_end_function is None:
            return
        if timer_id in self._timers:
            await timer_end_function()
