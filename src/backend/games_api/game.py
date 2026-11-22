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

from games_api.button import Button
from games_api.player import Player
from models.websocket import (
    MarkerData,
    ScoreboardData,
)

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

    ###############################################################################
    ################## inherited class must implement #############################
    ###############################################################################

    # have a start game function
    @abstractmethod
    async def start_game(self, config: dict[str, Any]) -> None:
        pass

    ###############################################################################
    #### inherited class does can change but must maintain this functionallity ####
    ###############################################################################

    # add scoreboard
    async def add_scoreboard(self,new_scoreboard:ScoreboardData):
        """
        Adds a new Scoreboad
        """
        self.scoreboard.append(new_scoreboard)

    # have a join lobby function
    async def join_lobby(self, player: Player) -> None:
        """
        The given player has joined the lobby
        """
        self.players_in_game.append(player)

    # have a leave lobby function
    async def leave_lobby(self, player: Player) -> None:
        """
        The given player has left the lobby
        """
        self.players_in_game.remove(player)

    def parse_message(player_id: UUID, room_id: UUID, message: str) -> tuple[UUID, UUID, str]:
        """
        Does the parsing of chat messages
        """
        tuple[player_id,room_id,message]




    ###############################################################################
    ################### inherited class does not change ###########################
    ###############################################################################

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
        """
        Asssign timers to a mass amount of players
        """
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
        """
        Gets all the scoreboards
        """
        return self.scoreboard

    # get_room(Room UUID): gets all the players that are in the chatroom
    def get_room(self, room_id: UUID) -> list[UUID]:
        """
        Gets all the players in the given room
        """
        if room_id in self.chat_room_players:
            return self.chat_room_players[room_id]
        else:
            return []

    #get way to add people to a room
    def add_to_room(self,room_id: UUID,players:list[Player]| None =None,read_permission=True, send_permission=True):
        """
        Adds a set of players to a room
        """
        if players is None:
            players =[]
        for player in players:
            player.assign_chatroom(room_id,read_permission, send_permission)
            self.chat_room_players[room_id].append(player.get_uuid())


    async def remove_from_room(self,room_id: UUID,players:list[Player]| None =None):
        """
        removs a set of given players from a room
        """
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
        """
        Mass send out of removing timers from each of given players
        """
        if players is None:
            players =[]
        for player in players:
            await player.stop_timer(timer_id)
        return True


    async def mass_notification_send(
        self,
        players:list[Player]| None =None,
        body:str | None = None,
        native: bool =False
    ):
        """
        Mass send out of notifications to each of given players
        """
        if players is None:
            players =[]
        for player in players:
            await player.send_notification(body,native)

    async def mass_scoreboard_update(
        self,
        players:list[Player]| None =None,
        scoreboard: list[ScoreboardData]|None = None
    )->None:
        """
        Mass send out of scoreboards to be updated to each of given players
        """
        if players is None:
            players =[]
        if scoreboard is None:
            scoreboard = []
        for player in players:
            await player._update_scoreboard(scoreboard)

    async def mass_scoreboard_delete(
        self,
        players:list[Player]| None =None,
        scoreboard: list[ScoreboardData]|None = None
    )->None:
        """
        Mass send out of scoreboards to be deleted to each of given players
        """
        if players is None:
            players =[]
        if scoreboard is None:
            scoreboard = []
        for player in players:
            await player._delete_scoreboard(scoreboard)

    async def mass_marker_update(
        self,
        players:list[Player]| None =None,
        markers:list[MarkerData]|None  = None
    )->None:
        """
        Mass send out of markers to be updated to each of given players
        """
        if players is None:
            players =[]
        if markers is None:
            markers = []
        for player in players:
            await player._update_marker(markers)


    async def mass_marker_delete(
        self,
        players:list[Player]| None =None,
        markers: list[MarkerData]|None  = None
    )->None:
        """
        Mass send out of markers to be deleted to each of given players
        """
        if players is None:
            players =[]
        if markers is None:
            markers = []
        for player in players:
            await player._delete_marker(markers)

    async def mass_button_update(
        self,
        players:list[Player]| None =None,
        buttons:list[Button]|None = None
    )->None:
        """
        Mass send out of buttons to be updated to each of given players
        """
        if players is None:
            players =[]
        if buttons is None:
            buttons = []
        for player in players:
            await player._update_button(buttons)

    async def mass_button_delete(
        self,
        players:list[Player]| None =None,
        buttons: list[Button]|None = None
    )->None:
        """
        Mass send out of buttons to be deleted to each of given players
        """
        if players is None:
            players =[]
        if buttons is None:
            buttons = []
        for player in players:
            await player._delete_button(buttons)
