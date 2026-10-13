from games_api import game
from games_api.player import Player
from typing import Any
from uuid import UUID
from .test_lobby import create_quick_lobby
from .test_user_modification import create_quick_user,get_uid_from_auth

from main import app
from fastapi import status
from fastapi.testclient import TestClient

client = TestClient(app)

def test_making_player():
    auth = create_quick_user()
    uuid = get_uid_from_auth(auth)
    try:
        player = Player(uuid)
    except NameError:
        assert(False)