from typing import Any
from uuid import UUID

from fastapi import status
from fastapi.testclient import TestClient

def create_quick_user(client: TestClient) -> str:
    """Helper method that creates a user. Returns an auth bearer string"""
    response = client.post("/v1/user/new")
    secret: str = response.json()["secret"]
    uuid: str = response.json()["id"]
    return f"Bearer {uuid}${secret}"


def create_quick_lobby(auth: str, client: TestClient, secret: str | None = None) -> UUID:
    """Helper method that creates a quick lobby given an auth string. Returns lobby uuid."""
    if secret is None:
        response = client.post("/v1/lobby/new", headers={"Authorization": auth})
    else:
        response = client.post(
            "/v1/lobby/new", params={"secret": secret}, headers={"Authorization": auth}
        )
    return UUID(response.json()["id"])


def get_uid_from_auth(auth: str) -> UUID:
    return UUID(auth.split(" ")[1].split("$")[0])


def get_user_info(auth: str, client: TestClient) -> dict[str, Any]:
    """Gets the public user info as from an auth bearer string"""
    response = client.get("/v1/user/info", params={"user_id": get_uid_from_auth(auth)})
    return response.json()


def join_lobby(auth: str, lobby_id: UUID, client: TestClient, lobby_secret: str | None = None) -> bool:
    """Trys to join the respective lobby at lobby_id with the
    user authenticated with auth. Returns true if joined successfully."""
    params = {
        "lobby_id": str(lobby_id),
    }
    if lobby_secret is not None:
        params["lobby_secret"] = lobby_secret
    response = client.post(
        "/v1/lobby/join", params=params, headers={"Authorization": auth}
    )
    print(response)
    print(response.json())
    return response.status_code == status.HTTP_200_OK

GARBAGE_AUTH_HEADERS = [
    {"Authorization": "Bearer Random Garbage"},
    {"Authorization": "Bearer "},
    {"Authorization": "Bea rer"},
    {"Authorization": "Bearer 01010101$010010001"},
    {"Auth": "Bearer 102948"},
    {"Authorization": "Bearer 01Ef12943jrka#$&@(!\x00\\EEE)"},
    {"Auth": "Bearer \x00\n\n\nHAHAHAHA"},
    {"Authorization": "Bearer \x00\n\n\nHAHAHAHA"},
]