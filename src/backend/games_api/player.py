"""
This file contains the Player sub-API for the Game API.
"""

from collections.abc import Callable
from typing import Any, TypeVar
from uuid import UUID

from db.engine import get_session
from db.models import User

T = TypeVar("T")


class Player:
    def __init__(self, uuid: UUID) -> None:
        self.uuid = uuid
        db_conn = get_session()
        user = db_conn.get(User, self.uuid)
        if user is None:
            raise ValueError
        self._user = user
        self._location = None

    def _set_location(self, new_location: tuple[float, float]) -> None:
        """
        Sets the location of the player.
        """
        self._location = new_location

    def get_name(self) -> str:
        """
        Gets the name of this player.
        """
        return self._user.name

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

    def send_notification(
        self, notification_title: str, notification_body: str | None = None
    ):
        """
        Sends a notification to a player. This is implied to be a in-app notification, but may
        also be a push notification if permission is available.
        """
        raise NotImplementedError("Notifications have not been implemented yet")

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
