from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any
from uuid import UUID

if TYPE_CHECKING:
    from player import Player


class Button:
    def __init__(
        self,
        uuid: UUID,
        button_function: Callable[[Player, list[str] | None], Any],
        button_name: str = "Unnamed Button",
        selection_function: Callable[[Player], list[list[str]]] | None = None,
    ):
        self.button_id = uuid
        self.function = button_function
        self.name = button_name
        self.selection = selection_function

    async def button_send(self, player_id: UUID, arguments: list[str]) -> None:
        pass

    async def button_fetch_args(self, player_id: Player) -> list[list[str]]:
        if self.selection is None:
            return []
        arguments = self.selection(player_id)
        if arguments is None:
            arguments = []
        return arguments
