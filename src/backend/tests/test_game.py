from typing import Any
from uuid import UUID

from fastapi import status
from fastapi.testclient import TestClient

from games_api import game
from games_api.player import Player
from main import app

from .test_lobby import create_quick_lobby
from .test_user_modification import create_quick_user, get_uid_from_auth,get_user_info

client = TestClient(app)

def test_making_player():
    auth = create_quick_user()
    uuid = get_uid_from_auth(auth)
    try:
        player = Player(uuid)
    except ValueError:
        assert(False)

def test_making_player_no_user():
    uuid = UUID(int=0)
    try:
        player = Player(uuid)
    except ValueError:
        pass
    else:
        assert(False)

def test_location():
    auth = create_quick_user()
    uuid = get_uid_from_auth(auth)
    player = Player(uuid)
    location = player.get_location()
    assert(location == None)
    old_location = (0.0,0.0)
    player._set_location(old_location)
    location = player.get_location()
    assert(location==old_location)
    new_location = (1.0,1.0)
    player._set_location(new_location)
    location = player.get_location()
    assert(location==new_location)

def test_name():
    auth = create_quick_user()
    user_name = get_user_info(auth)["name"]
    uuid = get_uid_from_auth(auth)
    player = Player(uuid)
    player_name = player.get_name()
    assert(user_name == player_name)
    