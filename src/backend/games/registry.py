"""
Every game adds them selves here so everthing can import the games
"""


from games_api.game import Game

GAMES: dict[str, type[Game]] = {}
