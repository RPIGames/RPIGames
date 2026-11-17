"""
This file contains the Game sub-API for the Game API.
Everything that shouldn't exist in any other sub-API
lives here.
"""

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any, ClassVar
from uuid import UUID

from games_api.player import Player
from models.websocket import ScoreboardData
import games_api.lobby

Type = type[str] | type[float] | type[int] | type[bool]


class Game(ABC):
    name: ClassVar[str]
    max_players: ClassVar[tuple[int, int]]
    game_config: ClassVar[dict[str, tuple[str, Type, str | float | int | bool | None]]]

    def __init__(self, initial_player: Player):
        self.scoreboard: list[ScoreboardData] = []
        self.chat_room_players: dict[UUID, list[UUID]] = {}
        self.players_in_game = list[Player] = []
        self.markers = list[MarkerData]=[]

    ##############################################################################
    ################## inherited class must implement ############################
    ##############################################################################
    # have a start game function
    @abstractmethod
    async def start_game(self, config: dict[str, Any]) -> None:
        pass

    ##############################################################################
    ### inherited class does can change but must maintain this functionallity ####
    ##############################################################################   
     
    # add scoreboard
    # takes in a sorted array that this then sends to front end.
    # takes in an amount of scores that are being stored
    # also takes the which score it is
    # also adds it to the list of scoreboards
    async def add_scoreboard(self,new_scoreboard:ScoreboardData):
        self.scoreboard.append(new_scoreboard)

    # have a join lobby function
    async def join_lobby(self, player: Player) -> None:
        await self.players_in_game.append(to_add)

    # have a leave lobby function
    async def leave_lobby(self, player: Player) -> None:
        await self.players_in_game.remove(to_add)

    

    ##############################################################################
    ################## inherited class does not change ###########################
    ##############################################################################
    # define function to get timers to all players
    async def assign_mass_timer(
        self,
        players: list[Player],
        timer_id: UUID,
        timer_end: datetime,
        timer_name: str = "Untitled Timer",
        timer_end_function: Callable[[], Awaitable[Any]] | None = None,
        disappear_on_completion: bool = True,
    ) -> bool:
        # add way to stop already started timers
        for player in players:
            await player.make_timer(
                timer_id,
                timer_end,
                timer_name,
                timer_end_function,
                disappear_on_completion,
            )
        return True

     # Scoreboard_request_all(Player UUID): this player has requested all scoreboards
    def scoreboard_get_all(
       self,
        player_UUID: UUID
        ) -> list[ScoreboardData]:
        return self.scoreboard

    # get_room(Room UUID): gets all the players that are in the chatroom
    def get_room(self, room_id: UUID) -> list[UUID]:
        if room_id in self.chat_room_players:
            return self.chat_room_players[room_id]
        else:
            return []
    
    #get way to add people to a room 
    def add_to_room(self,room_id: UUID,players:list[Player]| None =None,read_permission=True, send_permission=True):
        if players is None:
            players =[]
        for player in players:
            player.assign_chatroom(room_id,read_permission, send_permission)
            self.chat_room_players[room_id].append(player.get_uuid())
    
    #get way to remove people from a room 
    #takes in list of player that will be removed from the room
    #id of the room
    async def remove_from_room(self,room_id: UUID,players:list[Player]| None =None):
        if players is None:
            players =[]
        for player in players:
            await player.unassign_chatroom(room_id)
            self.chat_room_players[room_id].pop(player.get_uuid()|None)

    async def remove_mass_timer(
        self,
        timer_id: UUID,
        players:list[Player]| None =None
    )-> bool:
        if players is None:
            players =[]
        for player in players:
            await player.stop_timer(timer_id)
        return True

    async def mass_notification_Send(
        self,
        players:list[Player]| None =None,
        body:str | None = None,
        native: bool =False
    ):  
        if players is None:
            players =[]
        for player in players:
            await player.send_notification(body,native)

    async def mass_scoreboard_update(
        self,
        players:list[Player]| None =None
    )->None:
        if players is None:
            players =[]
        for player in players:
            await player._update_scoreboard(self.scoreboard)

    async def mass_scoreboard_delete(
        self,
        players:list[Player]| None =None
    )->None:
        if players is None:
            players =[]
        for player in players:
            await player._delete_scoreboard(self.scoreboard)

    async def mass_marker_update(
        self,
        players:list[Player]| None =None
    )->None:
        if players is None:
            players =[]
        for player in players:
            await player._update_marker(self.markers)

    async def mass_marker_update(
        self,
        players:list[Player]| None =None
    )->None:
        if players is None:
            players =[]
        for player in players:
            await player._delete_marker(self.markers)
    
    
    

