"""
This file contains tests for creating users,
as well as testing when users fail to be created
(for example, a bogus header)
"""

from typing import Any, Optional
from uuid import UUID

from fastapi import status
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def create_quick_user() -> str:
    """Helper method that creates a user. Returns an auth bearer string"""
    response = client.post("/v1/user/new")
    secret:str = response.json()["secret"]
    uuid:str = response.json()["id"]
    return f"Bearer {uuid}${secret}"

def create_quick_lobby(auth: str, *, secret: Optional[str] = None) -> UUID:
    """Helper method that creates a quick lobby given an auth string. Returns lobby uuid."""
    if secret is None:
        response = client.post("/v1/lobby/new", headers={'Authorization': auth})
    else:
        response = client.post("/v1/lobby/new", params={"secret": secret}, headers={'Authorization': auth})
    return UUID(response.json()["id"])

def get_uid_from_auth(auth:str) -> UUID:
    return UUID(auth.split(' ')[1].split('$')[0])

def get_user_info(auth: str) -> dict[str, Any]:
    """Gets the public user info as from an auth bearer string"""
    response = client.get("/v1/user/info", params={"user_id": get_uid_from_auth(auth)})
    return response.json()

def join_lobby(auth:str, lobby_id: UUID, lobby_secret: Optional[str] = None) -> bool:
    """Trys to join the respective lobby at lobby_id with the
    user authenticated with auth. Returns true if joined successfully."""
    params = {
        "lobby_id": str(lobby_id),
    }
    if lobby_secret is not None:
        params["lobby_secret"] = lobby_secret
    response = client.post("/v1/lobby/join", params=params, headers={'Authorization': auth})
    print(response)
    print(response.json())
    return response.status_code == status.HTTP_200_OK
    

def test_create_lobby():
    '''
    This test tests creating a lobby and getting info on that lobby.

    It sends a post request to the /lobby/new endpoint, and gets the
    user info returned when created. It checks for the following
    fields in the response:

    - id: the public user-id that anyone should be able to know
    - name: the name (randomly generated on creation) that the user contains
    - leader: a boolean containing if the user is a leader or not
    - lobby_id: the id of the lobby that the user has joined.
      Since the user hasn't been added to a lobby, it should be None
    '''
    auth = create_quick_user()
    assert "leader" in get_user_info(auth)
    assert bool == type(get_user_info(auth)["leader"])
    assert not get_user_info(auth)["leader"]
    assert "lobby_id" in get_user_info(auth)
    assert get_user_info(auth)["lobby_id"] is None
    assert "secret" not in get_user_info(auth)


    response = client.post("/v1/lobby/new", params={
        "name": "Test Lobby",
    }, headers= {'Authorization': auth})
    print(response.text)

    assert response.status_code == status.HTTP_200_OK
    
    assert "id" in response.json()
    lobby_id: str = response.json()["id"]
    lobby_id = UUID(lobby_id)
    assert response.json()["name"] == "Test Lobby"
    assert "max_members" in response.json()

def test_leave_lobby():
    """Tests the /leave endpoint"""
    auth = create_quick_user()
    lobby = create_quick_lobby(auth)
    assert get_user_info(auth)["leader"]
    assert get_user_info(auth)["lobby_id"] is not None
    
    response = client.post("/latest/lobby/leave", headers={'Authorization': auth})
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

    assert join_lobby(auth2, lobby_id=lobby)

    assert get_user_info(auth)["leader"]
    assert not get_user_info(auth2)["leader"]

    assert get_user_info(auth)["lobby_id"] == get_user_info(auth2)["lobby_id"]
    assert get_user_info(auth)["lobby_id"] is not None
    assert get_user_info(auth2)["lobby_id"] is not None

def test_grant_leadership():
    """Tests the /lobby/leadership/grant endpoint"""
    auth = create_quick_user()
    lobby = create_quick_lobby(auth)
    auth2 = create_quick_user()
    assert join_lobby(auth2, lobby)

    assert get_user_info(auth)["leader"]
    assert get_user_info(auth)["lobby_id"] is not None
    assert not get_user_info(auth2)["leader"]

    response = client.post("/latest/lobby/leadership/grant", 
        params={"grantee_id": get_uid_from_auth(auth2)}, 
        headers={"Authorization": auth}
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

    assert join_lobby(auth2, lobby_id=lobby, lobby_secret="testsecret")

    assert get_user_info(auth)["leader"]
    assert not get_user_info(auth2)["leader"]

    assert get_user_info(auth)["lobby_id"] == get_user_info(auth2)["lobby_id"]
    assert get_user_info(auth)["lobby_id"] is not None
    assert get_user_info(auth2)["lobby_id"] is not None
