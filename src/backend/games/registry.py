"""
Every game adds them selves here so everthing can import the games
"""

import games_api.game 

GAMES: dict[str, type[ games_api.game.Game]] = {}
