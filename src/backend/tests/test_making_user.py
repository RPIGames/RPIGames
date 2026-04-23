from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_create_user():
    response = client.post("/user/new")
    assert response.status_code == 200
    assert "secret" in response.json()

    secret:str = response.json()["secret"]

    response = client.get("/user/info", headers={'Authorization': f"Bearer {secret}"})
    assert response.status_code == 200
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
    print(response.json())
    assert None == response.json()["lobby_id"]
    