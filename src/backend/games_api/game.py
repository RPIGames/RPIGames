"""
This file contains the Game sub-API for the Game API.
Everything that shouldn't exist in any other sub-API
lives here.
"""

from abc import ABC, abstractmethod

from collections.abc import Awaitable, Callable
from typing import Any, ClassVar
from uuid import UUID
from datetime import datetime
from collections.abc import Callable

from games_api.player import Player

Type = type[str] | type[float] | type[int] | type[bool]

class Game(ABC):

    name: ClassVar[str]
    max_players: ClassVar[tuple[int, int]]
    game_config: ClassVar[dict[str, tuple[str, Type, str | float | int | bool | None]]]

    def __init__(self, initial_player: Player):
        self.scoreboard = []
        self.chat_room_players :dict[UUID,List[UUID]] = {}
        


    #add scoreboard
    #takes in a sorted array that this then sends to front end.
    #takes in an amount of scores that are being stored
    #also takes the which score it is
    #also adds it to the list of scoreboards

    #Scoreboard_request_all(Player UUID): this player has requested all scoreboards
    #async def scoreboard_get_all(
    #   self,
    #    player_UUID: str | UUID
    #    ) -> list[ScoreboardData]:
    #    return self.scoreboard

    #Chat_Send_Message(Room UUID, message): gets all the players that are in the chatroom 
    async def get_room(self,
        room_id: UUID) -> list[UUID]:
        if room_id in self.chat_room_players:
            return self.chat_room_players[room_id]

    #have a start game function

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
    
    #define function to get timers to all players
    async def assign_mass_timer(self,
        players: list[Player],
        timer_id : UUID,
        timer_end: datetime,
        timer_name: str = "Untitled Timer",
        timer_end_function: Callable[[],Awaitable[Any] ] | None = None,
        disappear_on_completion: bool = True
        )-> bool:
        #add way to stop already started timers
        for player in players:
            if(player.make_timer(timer_id,timer_end,timer_name,timer_end_function,disappear_on_completion)!=tuple[timer_id,timer_end,timer_name,timer_end_function,disappear_on_completion ]):
                return False
        return True
