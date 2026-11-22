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
from games_api.button import Button
from games_api.schedule import schedule
from models.websocket import (
    ButtonData,
    ChatroomData,
    LocationData,
    MarkerData,
    ScoreboardData,
    TimerData,
)

T = TypeVar("T")

_timers: dict[ Player,dict[
            UUID, tuple[TimerData, Callable[[], Awaitable[Any]] | None]
        ] ]= {}
_location: dict[Player,LocationData|None]={}
_buttons: dict[Player,dict[UUID,Button|None]]={}

def _get_user_from_uuid(uuid: UUID) -> User | None:
    user = None
    with Session(engine) as db_conn:
        user = db_conn.get(User, uuid)
    if user is None:
        raise ValueError
    return user

class Player:
    def __init__(self, uuid: UUID) -> None:
        self.uuid = uuid
        # test for validity
        _get_user_from_uuid(uuid)

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
        user = _get_user_from_uuid(self.uuid)

        assert user is not None
        return user.name

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

    async def assign_chatroom(
        self, chatroom_id: UUID,chatroom_name: str, read_permission=True, send_permission=True
    ):
        """
        Assigns a chatroom to the player, so that the player can see it.
        """
        temp_chatroom = [ChatroomData(name =chatroom_name,room_id =  chatroom_id, read =read_permission, write =  send_permission)]
        await  routers.v1.websocket.manager.update_chatrooms([self.uuid],temp_chatroom)

    async def update_chatroom(
        self, chatroom_id: UUID,chatroom_name: str, read_permission=True, send_permission=True
    ):
        """
        Updates a chatroom to the player, so that the player can see it.
        """

        temp_chatroom = [ChatroomData(name =chatroom_name,room_id =  chatroom_id, read =read_permission, write =  send_permission)]
        await  routers.v1.websocket.manager.update_chatrooms([self.uuid],temp_chatroom)

    #get chatrooms in
    async def unassign_chatroom(self, chatroom_id: UUID,):
        """
        Unassigns a chatroom to the player, so that the player stops seeing it.
        """
        temp_chatroom  = [chatroom_id]
        await  routers.v1.websocket.manager.delete_chatroom(self.uuid,temp_chatroom)

    async def send_notification(
        self,
        notification: str,
        native: bool = False,
    ):
        """
        Sends a notification to a player. This is implied to be a in-app notification, but may
        also be a push notification if permission is available.
        """
        await routers.v1.websocket.manager.send_notification(self.uuid,notification,native)
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
        """
        Requeast all the timers this player knows
        """
        timers_list: list[TimerData] = []
        for timer in _timers[self]:
            timers_list.append(_timers[self][timer][0])
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
        scoreboard_ids = []
        for scoreboard in scoreboards:
            scoreboard_ids.append(scoreboard.id)
        await routers.v1.websocket.manager.delete_scoreboards(self.uuid,scoreboard_ids)

    async def _update_marker(
        self,
        markers: list[MarkerData]
    )-> None:
        await routers.v1.websocket.manager.update_markers(self.uuid,markers)

    async def _delete_marker(
        self,
        markers: list[MarkerData]
    )-> None:
        marker_ids = []
        for marker in markers:
            marker_ids.append(marker.id)
        await routers.v1.websocket.manager.delete_markers(self.uuid,marker_ids)

    async def _update_button(self, buttons:list[Button])-> None:
        temp_button: list[ButtonData] = []
        for button in buttons:
            _buttons[self][button.get_uuid()] = button
            temp_button.append(button.make_button_data())
        await routers.v1.websocket.manager.update_buttons([self.uuid], temp_button)

    async def _delete_button(self, buttons: list[Button])-> None:
        temp_button: list[UUID] = []
        for button in buttons:
            _buttons[self].pop(button.get_uuid())
            temp_button.append(button.button_id)
        await routers.v1.websocket.manager.delete_buttons([self.uuid], temp_button)
