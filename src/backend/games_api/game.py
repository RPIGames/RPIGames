"""
This file contains the Game sub-API for the Game API.
Everything that shouldn't exist in any other sub-API
lives here.
"""

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from games_api.player import Player

Type = type[str] | type[float] | type[int] | type[bool]

class Game(ABC):

    name: ClassVar[str]
    max_players: ClassVar[tuple[int, int]]
    game_config: ClassVar[dict[str, tuple[str, Type, str | float | int | bool | None]]]

    def __init__(self, initial_player: Player):
        self.scoreboard = []


    #add scoreboard
    #takes in a sorted array that this then sends to front end.
    #takes in an amount of scores that are being stored
    #also takes the which score it is
    #also adds it to the list of scoreboards
    #Scoreboard_request_all(Player UUID): this player has requested all scoreboards

    # async def scoreboard_get_all(
    #    self,
    #    player_UUID: str | UUID
    #    ) -> list[ScoreboardData]:
    #    return scoreboard
    #have a start game function

    @abstractmethod
    async def start_game(self, config: dict[str, Any]) -> None:
        pass

    #have a join lobby funtion
    @abstractmethod
    async def join_lobby(self, player: Player) -> None:
        pass


    # have a leave lobby funtion
    @abstractmethod
    async def leave_lobby(self, player: Player) -> None:
        pass

    #All of these the children class can not change
