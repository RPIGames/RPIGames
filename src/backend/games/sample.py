"""
Here's a sample game made using the Game API.
This shouldn't work until we get the API implemented.
"""

from random import shuffle
from typing import Annotated, Any, ClassVar, TypedDict
from uuid import UUID

from games_api import game
from games_api.player import Player


class SampleGameConfig(TypedDict):
    welcome_message: Annotated[str, "Welcome message"]


class SampleGame:
    game_config: ClassVar[dict[str, tuple[str, type]]] = {
        "welcome_message": ("Welcome message", str),
        "time_to_hide": ("Time to Hide (minutes):", int),
        "points_for_hiding": ("Points per minute hidden:", int),
        "points_for_seeking": ("Points per hider found:", int),
    }

    async def __init__(self, lobby_id: UUID, initial_player: Player) -> None:
        self.unassigned_players = [initial_player]
        self.game_started = False
        self.hiders: list[Player] = []
        self.seekers: list[Player] = []
        self.scores: dict[UUID, int] = {}

    async def start_game(self, config: dict[str, Any]) -> None:
        shuffle(self.unassigned_players)
        self.seekers.append(self.unassigned_players.pop())
        while len(self.unassigned_players) > 0:
            self.hiders.append(self.unassigned_players.pop())

        self.hide_time: int = config["time_to_hide"]
        self.points_per_player = config["points_for_seeking"]
        self.points_per_min_hide = config["points_for_hiding"]

        for player in self.hiders:
            player.send_notification(
                "Time to hide!",
                f"""
                The game has started. You are a hider. Start hiding, you have {self.hide_time} minutes.
            """,
            )

        for player in self.seekers:
            player.send_notification(
                "Stay Put!",
                """
                You are a seeker. Stay put for now, and watch the timer. Once the timer finishes, you can begin seeking.
            """,
            )

        game.schedule(self.hide_time, self._wait_time_ended)

        self.game_started = True

    async def _wait_time_ended(self):
        for seeker in self.seekers:
            seeker.send_notification(
                "Time to seek!", """The timer is up and you can start seeking."""
            )
        for hider in self.hiders:
            hider.send_notification(
                "Hide!", """The seekers have been released. Good luck. """
            )
            hider.assign_button(
                "button_join",
                self.button_found_me,
                selection=self.seekers,
                button_name="Found Me",
            )

    async def join_lobby(self, player: Player) -> None:
        if self.game_started:
            self.seekers.append(player)

            player.send_notification(
                "Welcome to the game!",
                """
            You are a seeker, go find the hiders!
            """,
            )
        else:
            self.unassigned_players.append(player)
            player.send_notification(
                "Welcome to the game!",
                """
            The game is still starting, wait for the team leader.
            """,
            )

    async def button_found_me(self, player: Player, selection: Player):
        self.hiders.remove(player)
        self.seekers.append(player)

        if selection.uuid not in self.scores:
            self.scores[selection.uuid] = 0
        self.scores[selection.uuid] += self.points_per_player

        selection.send_notification("You found a player!")
