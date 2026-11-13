from datetime import datetime
from uuid import UUID

import pytest

from games_api.player import Player
from models.websocket import LocationData

from .helper import create_quick_user, get_uid_from_auth, get_user_info


def test_making_player():
    """
    test making a player in general
    """
    auth = create_quick_user()
    uuid = get_uid_from_auth(auth)
    try:
        player = Player(uuid)
        assert player.uuid == uuid
    except ValueError:
        assert False


def test_making_player_no_user():
    """
    Test making a player if there is no user requested
    """
    uuid = UUID(int=0)
    try:
        player = Player(uuid)
        assert player.uuid == uuid
    except ValueError:
        pass
    else:
        assert False


# when websockets are implemented fix to test wider variety
@pytest.mark.anyio
async def test_location():
    """
    Test the location to see what happens there is not a location and checking to see location overided correctly.
    """
    auth = create_quick_user()
    uuid = get_uid_from_auth(auth)
    player = Player(uuid)
    location = player.get_location()
    assert location == None
    old_location = LocationData(accuracy=0.0, latitude=0.0,longitude=0.0,time=datetime.now())
    await player._set_location(old_location)
    location = player.get_location()
    assert location == old_location
    new_location = LocationData(accuracy=1.0, latitude=1.0,longitude=1.0,time=datetime.now())
    await player._set_location(new_location)
    location = player.get_location()
    assert location == new_location


def test_name():
    """
    test to make sure that player gets name correctly.
    """
    auth = create_quick_user()
    user_name = get_user_info(auth)["name"]
    uuid = get_uid_from_auth(auth)
    player = Player(uuid)
    player_name = player.get_name()
    assert user_name == player_name
