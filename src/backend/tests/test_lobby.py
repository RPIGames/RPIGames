"""
This file contains tests for creating users,
as well as testing when users fail to be created
(for example, a bogus header)
"""

from uuid import UUID

from fastapi import status
from fastapi.testclient import TestClient

from .helper import create_quick_user, create_quick_lobby, get_uid_from_auth, get_user_info, join_lobby
from main import app

client = TestClient(app)

def test_create_lobby():
    """
    This test tests creating a lobby and getting info on that lobby.

    It sends a post request to the /lobby/new endpoint, and gets the
    user info returned when created. It checks for the following
    fields in the response:

    - id: the public user-id that anyone should be able to know
    - name: the name (randomly generated on creation) that the user contains
    - leader: a boolean containing if the user is a leader or not
    - lobby_id: the id of the lobby that the user has joined.
      Since the user hasn't been added to a lobby, it should be None
    """
    auth = create_quick_user(client)
    assert "leader" in get_user_info(auth, client)
    assert isinstance(get_user_info(auth, client)["leader"], bool)
    assert not get_user_info(auth, client)["leader"]
    assert "lobby_id" in get_user_info(auth, client)
    assert get_user_info(auth, client)["lobby_id"] is None
    assert "secret" not in get_user_info(auth, client)

    response = client.post(
        "/v1/lobby/new",
        params={
            "name": "Test Lobby",
        },
        headers={"Authorization": auth},
    )
    print(response.text)

    assert response.status_code == status.HTTP_200_OK

    assert "id" in response.json()
    lobby_id_str: str = response.json()["id"]
    _lobby_id = UUID(lobby_id_str)
    assert response.json()["name"] == "Test Lobby"
    assert "max_members" in response.json()


def test_leave_lobby():
    """Tests the /leave endpoint"""
    auth = create_quick_user(client)
    _lobby = create_quick_lobby(auth, client)
    assert get_user_info(auth, client)["leader"]
    assert get_user_info(auth, client)["lobby_id"] is not None

    response = client.post("/latest/lobby/leave", headers={"Authorization": auth})
    assert response.status_code == status.HTTP_200_OK
    assert "error" not in response.json()

    assert get_user_info(auth, client)["lobby_id"] is None
    assert not get_user_info(auth, client)["leader"]


def test_join_lobby():
    """Tests both creating and joining a public lobby"""
    auth = create_quick_user(client)
    lobby = create_quick_lobby(auth, client)

    auth2 = create_quick_user(client)
    assert get_user_info(auth2, client)["lobby_id"] is None

    assert join_lobby(auth2, lobby, client)

    assert get_user_info(auth, client)["leader"]
    assert not get_user_info(auth2, client)["leader"]

    assert get_user_info(auth, client)["lobby_id"] == get_user_info(auth2, client)["lobby_id"]
    assert get_user_info(auth, client)["lobby_id"] is not None
    assert get_user_info(auth2, client)["lobby_id"] is not None


def test_grant_leadership():
    """Tests the /lobby/leadership/grant endpoint"""
    auth = create_quick_user(client)
    lobby = create_quick_lobby(auth, client)
    auth2 = create_quick_user(client)
    assert join_lobby(auth2, lobby, client)

    assert get_user_info(auth, client)["leader"]
    assert get_user_info(auth, client)["lobby_id"] is not None
    assert not get_user_info(auth2, client)["leader"]

    response = client.post(
        "/latest/lobby/leadership/grant",
        params={"grantee_id": get_uid_from_auth(auth2)},
        headers={"Authorization": auth},
    )

    assert response.status_code == 200

    assert not get_user_info(auth, client)["leader"]
    assert get_user_info(auth2, client)["leader"]


def test_join_hidden_lobby():
    """Tests both creating and joining a private lobby"""
    auth = create_quick_user(client)
    lobby = create_quick_lobby(auth, client, secret="testsecret")

    auth2 = create_quick_user(client)
    assert get_user_info(auth2, client)["lobby_id"] is None

    assert join_lobby(auth2, lobby, client, lobby_secret="testsecret")

    assert get_user_info(auth, client)["leader"]
    assert not get_user_info(auth2, client)["leader"]

    assert get_user_info(auth, client)["lobby_id"] == get_user_info(auth2, client)["lobby_id"]
    assert get_user_info(auth, client)["lobby_id"] is not None
    assert get_user_info(auth2, client)["lobby_id"] is not None
