from fastapi import status
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_create_user():
    response = client.post("/user/new")
    assert response.status_code == status.HTTP_200_OK
    assert "secret" in response.json()

    secret:str = response.json()["secret"]

    response = client.get("/user/info", headers={'Authorization': f"Bearer {secret}"})
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

    response = client.post(url="/user/new", headers={'Authorization': f"Bearer {secret}"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "You are already sending a valid user token"
    }

def test_create_with_random_garbage_auth_header():

    response = client.post(url="/user/new", headers={'Authorization': "Bearer Random Garbage"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "You are already sending a valid user token"
    }

    response = client.post(url="/user/new", headers={'Authorization': "Bearer "})
    assert response.status_code == status.HTTP_200_OK
    assert "secret" in response.json()

    response = client.post(url="/user/new", headers={'Authorization': "Bea rer"})
    assert response.status_code == status.HTTP_200_OK
    assert "secret" in response.json()

    response = client.post(url="/user/new", headers={'Authorization': "Bearer 01010101010010001"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "You are already sending a valid user token"
    }

    response = client.post(url="/user/new", headers={'Auth': "Bearer 102948"})
    assert response.status_code == status.HTTP_200_OK
    assert "secret" in response.json()

    response = client.post(url="/user/new", headers={'Authorization': "Bearer 01Ef12943jrka#$&@(!\x00\\EEE)"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "You are already sending a valid user token"
    }

    response = client.post(url="/user/new", headers={'Auth': "Bearer \x00\n\n\nHAHAHAHA"})
    assert response.status_code == status.HTTP_200_OK
    assert "secret" in response.json()

def test_user_info_with_garbage():

    response = client.get(url="/user/info", headers={'Authorization': "Bearer Randomjaje00Gabage"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
