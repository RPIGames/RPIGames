"""
This file contains tests for creating users,
as well as testing when users fail to be created
(for example, a bogus header)
"""

from uuid import UUID

from fastapi import status

from .helper import (
    client,
    create_quick_lobby,
    create_quick_user,
    get_uid_from_auth,
    get_user_info,
    join_lobby,
)


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
    auth = create_quick_user()
    assert "leader" in get_user_info(auth)
    assert isinstance(get_user_info(auth)["leader"], bool)
    assert not get_user_info(auth)["leader"]
    assert "lobby_id" in get_user_info(auth)
    assert get_user_info(auth)["lobby_id"] is None
    assert "secret" not in get_user_info(auth)

    response = client.post(
        "/v1/lobby/new",
        json={
            "name": "Test Lobby",
            "game_type_id": "sample_game",
            "game_capacity": 8,
            "game_config": {
                "welcome_message": "hello",
                "time_to_hide": 5,
                "points_for_hiding": 10,
                "points_for_seeking": 15,
            }
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
    auth = create_quick_user()
    _lobby = create_quick_lobby(auth)
    assert get_user_info(auth)["lobby_id"] is not None
    assert get_user_info(auth)["leader"]

    response = client.post("/latest/lobby/leave", headers={"Authorization": auth})
    assert response.status_code == status.HTTP_200_OK
    assert "error" not in response.json()

    assert get_user_info(auth)["lobby_id"] is None
    assert not get_user_info(auth)["leader"]


def test_join_lobby():
    """Tests both creating and joining a public lobby"""
    auth = create_quick_user()
    lobby = create_quick_lobby(auth)

    auth2 = create_quick_user()
    assert get_user_info(auth2)["lobby_id"] is None

    assert join_lobby(auth2, lobby)

    assert get_user_info(auth)["leader"]
    assert not get_user_info(auth2)["leader"]

    assert get_user_info(auth)["lobby_id"] == get_user_info(auth2)["lobby_id"]
    assert get_user_info(auth)["lobby_id"] is not None
    assert get_user_info(auth2)["lobby_id"] is not None


def test_grant_leadership():
    """Tests the /lobby/leadership/grant endpoint"""
    auth = create_quick_user()
    lobby = create_quick_lobby(auth, )
    auth2 = create_quick_user()
    assert join_lobby(auth2, lobby, )

    assert get_user_info(auth)["leader"]
    assert get_user_info(auth)["lobby_id"] is not None
    assert not get_user_info(auth2)["leader"]

    response = client.post(
        "/latest/lobby/leadership/grant",
        headers={"Authorization": auth},
        json={"grantee_id": str(get_uid_from_auth(auth2))},
    )

    assert response.status_code == 200

    assert not get_user_info(auth)["leader"]
    assert get_user_info(auth2)["leader"]


def test_join_hidden_lobby():
    """Tests both creating and joining a private lobby"""
    auth = create_quick_user()
    lobby = create_quick_lobby(auth, secret="testsecret")

    auth2 = create_quick_user()
    assert get_user_info(auth2)["lobby_id"] is None

    assert join_lobby(auth2, lobby, lobby_secret="testsecret")

    assert get_user_info(auth)["leader"]
    assert not get_user_info(auth2)["leader"]

    assert get_user_info(auth)["lobby_id"] == get_user_info(auth2)["lobby_id"]
    assert get_user_info(auth)["lobby_id"] is not None
    assert get_user_info(auth2)["lobby_id"] is not None
