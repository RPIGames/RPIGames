"""
This file contains the Player sub-API for the Game API.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any, TypeVar
from uuid import UUID

from sqlmodel import Session

import routers.v1.websocket
from db.engine import engine
from db.models import User
from games_api.schedule import schedule
from models.websocket import LocationData, TimerData

T = TypeVar("T")

_timers: dict[ Player,dict[
            UUID, tuple[TimerData, Callable[[], Awaitable[Any]] | None]
        ] ]= {}
_location: dict[Player,LocationData|None]={}
class Player:
    def __init__(self, uuid: UUID) -> None:
        self.uuid = uuid
        db_conn = Session(engine)
        user = db_conn.get(User, self.uuid)
        if user is None:
            raise ValueError
        self._user = user
        self._location = None
        

    def __eq__(self, value: object, /) -> bool:
        if type(value) is Player:
            return value.uuid == self.uuid
        return False

    def __hash__(self)->int:
        return self.uuid.__hash__()

    # when websockets are implemented fix deal with right type of location
    async def _set_location(self, new_location: LocationData) -> None:
        """
        Sets the location of the player.
        """
        _location[self] = new_location

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
        try:
            return _location[self]
        except KeyError:
            _location[self] = None
            return None
        

    def get_uuid(self)->UUID:
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

    async def send_notification(
        self,
        notification_title: str,
        notification_body: str | None = None,
        native: bool = False,
    ):
        """
        Sends a notification to a player. This is implied to be a in-app notification, but may
        also be a push notification if permission is available.
        """
        await routers.v1.websocket.manager.send_notification(self.uuid,notification_body,native)
        #raise NotImplementedError("Notifications have not been implemented yet")

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
        
        _timers[self][timer_id] = ( 
            TimerData(id=timer_id,
            name=timer_name,
            time=timer_end,
            disappear_on_completion=disappear_on_completion),
            timer_end_function,
        )
        amount_of_seconds = timer_end.timestamp() - (datetime.now()).timestamp()
        amount_of_seconds = amount_of_seconds / 60
        schedule(amount_of_seconds, self._check_timer, timer_id, timer_end_function)
        return ( 
            TimerData(id=timer_id,
            name=timer_name,
            time=timer_end,
            disappear_on_completion=disappear_on_completion),
            timer_end_function,
        )

    # Timer_request_all(): this player has requested all timers
    def _timer_request_all(
        self,
    ) -> list[
        TimerData
    ]:
        timers_list = []
        for timer in _timers[self]:
            timers_list.append(timer[0])
        return timers_list

    # stop timer
    async def stop_timer(self, timer_id: UUID):
        """
        Tries to remove the time if the timer does not exist return false otherwise return true
        """
        checking = _timers[self].pop(timer_id, None)
        return checking != None

    
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
        if timer_id in _timers[self]:
            await timer_end_function()

    async def _update_scoreboard(
        self,
        scoreboards: list[ScoreboardData]
    ) -> None:
        await routers.v1.websocket.manager.update_scoreboards(self.uuid,scoreboards)
        
    async def _delete_scoreboard(
        self,
        scoreboards: list[ScoreboardData]
    ) -> None:
        await routers.v1.websocket.manager.delete_scoreboards(self.uuid,scoreboards)

    async def _update_marker(
        self,
        markers: List[MarkerData]
    )-> None:
        await routers.v1.websocket.manager.update_markers(self,markers)
    
    async def _delete_marker(
        self,
        markers: List[MarkerData]
    )-> None:
        await routers.v1.websocket.manager.delete_markers(self,markers)