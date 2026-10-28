"""
This file contains the Lobby class, handling lobby data. A lobby contains a constructed game,
and a list of players that are in the lobby.
"""

from random import choice, randint
from uuid import UUID, uuid4

from games.registry import GAMES
from games_api.player import Player
from games_api.private_maps import PLAYER_TO_LOBBY_MAP


class Lobby:
    def __init__(self,
        game_name: str,
        game_settings: dict[str, str | float | int | bool],
        leader: Player,
        lobby_size: int,
        name: str = f"Unnamed Lobby {randint(1000, 9999)}",
        secret: str | None = None,
    ) -> None:
        if game_name not in GAMES:
            raise ValueError("invalid game_type")

        game_type = GAMES[game_name]

        for config_option in game_type.game_config.items():
            if config_option[0] not in game_settings:
                raise ValueError(f"{config_option[0]} not in game_settings")
            if type(game_settings[config_option[0]]) is not config_option[1][1]:
                raise TypeError(f"{config_option[0]} is not of required type f{type(config_option[1])}")

        self._uuid = uuid4()
        PLAYER_TO_LOBBY_MAP[leader.uuid] = self._uuid
        GLOBAL_LOBBY_MAP[self._uuid] = self
        self._players = [leader]
        self.leader = leader
        self.capacity = lobby_size
        self.name = name
        self.secret = secret

        self._game = game_type(leader)

    def get_players(self) -> list[Player]:
        return self._players

    async def add_player(self, to_add: Player) -> None:
        if len(self._players) == self.capacity:
            raise ValueError("the lobby is full")

        self._players.append(to_add)
        PLAYER_TO_LOBBY_MAP[to_add.uuid] = self._uuid
        await self._game.join_lobby(to_add)

    async def remove_player(self, to_remove: Player) -> None:
        await self._game.leave_lobby(to_remove)

        self._players.remove(to_remove)
        PLAYER_TO_LOBBY_MAP.pop(to_remove.uuid)


        if len(self._players) == 0:
            # here we need to delete the lobby
            GLOBAL_LOBBY_MAP.pop(self._uuid)
        elif (self.leader == to_remove):
            self.leader = choice(self._players)

        assert self.leader != to_remove or GLOBAL_LOBBY_MAP.get(self._uuid) is None



GLOBAL_LOBBY_MAP: dict[UUID, Lobby] = {}

def get_players_lobby(player: Player) -> Lobby | None:
    lobby_id = PLAYER_TO_LOBBY_MAP.get(player.uuid)

    if lobby_id is None:
        return None

    lobby = GLOBAL_LOBBY_MAP.get(lobby_id)

    if lobby is None:
        PLAYER_TO_LOBBY_MAP.pop(player.uuid)
        return None

    return lobby
