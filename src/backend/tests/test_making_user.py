"""
This file contains tests for creating users,
as well as testing when users fail to be created
(for example, a bogus header)
"""

from fastapi import status
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_create_user():
    '''
    This test tests creating a new user and getting info on the user.

    It sends a post request to the /user/new endpoint, and gets the
    user info returned when created. It checks for the following
    fields in the response:

    - id: the public user-id that anyone should be able to know
    - secret: the secret user-key that only the user should be able to know
    - name: the name (randomly generated on creation) that the user contains
    - leader: a boolean containing if the user is a leader or not
    - lobby_id: the id of the lobby that the user has joined.
      Since the user hasn't been added to a lobby, it should be None/NULL
    '''
    response = client.post("/user/new")
    assert response.status_code == status.HTTP_200_OK
    assert "secret" in response.json()
    assert "id" in response.json()

    secret:str = response.json()["secret"]
    uuid:str = response.json()["id"]

    response = client.get("/user/info", headers={'Authorization': f"Bearer {uuid}${secret}"})
    assert response.status_code == status.HTTP_200_OK
    assert "id" in response.json()
    assert str == type(response.json()["id"])
    assert "secret" in response.json()
    assert str == type(response.json()["secret"])
    assert "name" in response.json()
    assert str == type(response.json()["name"])
    assert "leader" in response.json()
    assert bool == type(response.json()["leader"])
    assert not response.json()["leader"]
    assert "lobby_id" in response.json()
    assert None == response.json()["lobby_id"]

def test_create_already_signed_in():
    '''
    This test tests creating a new user and trying to create another user with the user
    already created.

    It sends a post request to the /user/new endpoint, and then
    does it again with the Bearer that the endpoint returned.

    It then asserts that it returns an 400 error.
    '''
    response = client.post("/user/new")
    assert response.status_code == status.HTTP_200_OK
    assert "secret" in response.json()

    secret:str = response.json()["secret"]
    uuid:str = response.json()["id"]

    response = client.post(url="/user/new", headers={'Authorization': f"Bearer {uuid}${secret}"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "You are already sending a valid user token"
    }

GARBAGE_AUTH_HEADERS = [
    {'Authorization': "Bearer Random Garbage"},
    {'Authorization': "Bearer "},
    {'Authorization': "Bea rer"},
    {'Authorization': "Bearer 01010101$010010001"},
    {'Auth': "Bearer 102948"},
    {'Authorization': "Bearer 01Ef12943jrka#$&@(!\x00\\EEE)"},
    {'Auth': "Bearer \x00\n\n\nHAHAHAHA"},
]

def test_create_with_random_garbage_auth_header():
    '''
    This test tests creating a new user with garbage authentication headers.

    Since the authentication headers aren't user tokens, they should return
    the new user token.
    '''
    for auth in GARBAGE_AUTH_HEADERS:
        response = client.post(url="/user/new", headers=auth)
        assert response.status_code == status.HTTP_200_OK
        assert "id" in response.json()
        assert "secret" in response.json()

def test_user_info_with_garbage():
    '''
    This test tests fetching user info with garbage authentication headers.

    Since the authentication headers aren't user tokens, they should return
    400 bad request errors.
    '''
    for auth in GARBAGE_AUTH_HEADERS:
        response = client.get(url="/user/info", headers={'Authorization': "Bearer Randomjaje00Gabage"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
