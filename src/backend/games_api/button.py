from collections.abc import Callable
from typing import Any, T
from uuid import UUID


class Button:
    def __init__(self,
     uuid: UUID,
     button_function: Callable[["Player", T], Any],
     button_name: str = "Unnamed Button",
     selection_function: Callable[["Player"], list[list[str]]]|None =None,
     ):
     self.button_id = uuid
     self.function = button_function
     self.name =  button_name
     self.selection = selection_function

    async def button_send(self,player_id: UUID, arguments: list[str]) -> None:
        pass

    async def button_fetch_args(self,player_id: "Player") -> list[list[str]]:
        return self.selection(player_id)
