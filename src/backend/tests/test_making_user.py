from fastapi import status
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_create_user():
    response = client.post("/user/new")
    assert response.status_code == status.HTTP_200_OK
    assert "secret" in response.json()

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

    for auth in GARBAGE_AUTH_HEADERS:
        response = client.post(url="/user/new", headers=auth)
        assert response.status_code == status.HTTP_200_OK
        assert "id" in response.json()
        assert "secret" in response.json()

def test_user_info_with_garbage():

    for auth in GARBAGE_AUTH_HEADERS:
        response = client.get(url="/user/info", headers={'Authorization': "Bearer Randomjaje00Gabage"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
