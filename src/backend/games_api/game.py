"""
This file contains the Game sub-API for the Game API.
Everything that shouldn't exist in any other sub-API
lives here.
"""

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID
from abc import ABC,abstractmethod



class Game(ABC):
    players =[]#replace with double hash map b/w players and games
    scoreboard = []
    def __init__(self, lobby_id: UUID):
        self._lobby_id = lobby_id

    
    #add scoreboard
    #takes in a sorted array that this then sends to front end.
    #takes in an amount of scores that are being stored
    #also takes the which score it is 
    #also adds it to the list of scoreboards
    #Scoreboard_request_all(Player UUID): this player has requested all scoreboards

    async def Scoreboard_get_all(
       self,
       player_UUID: str | UUID
       ) -> list[ScoreboardData]:
       return scoreboard
    #have a start game function
    @abstractmethod
    async def start_game(self, config: dict[str, Any]) -> None:
        pass

    #have a join lobby funtion 
    @abstractmethod
    async def join_lobby(self, player: Player) -> None:
        pass

    #All of these the children class can not change
	



