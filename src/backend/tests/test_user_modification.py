"""
This file contains tests for creating users,
as well as testing when users fail to be created
(for example, a bogus header)
"""

from typing import Any
from uuid import UUID

from fastapi import status
from fastapi.testclient import TestClient

from models.response import ErrorResponse, AuthenticationErrorResponse
from main import app

client = TestClient(app)

def create_quick_user() -> str:
    """Helper method that creates a user. Returns an auth bearer string"""
    response = client.post("/v1/user/new")
    secret:str = response.json()["secret"]
    uuid:str = response.json()["id"]
    assert response.status_code == status.HTTP_200_OK
    return f"Bearer {uuid}${secret}"

def get_uid_from_auth(auth:str) -> UUID:
    return UUID(auth.split(' ')[1].split('$')[0])

def get_user_info(auth: str) -> dict[str, Any]:
    """Gets the public user info as from an auth bearer string"""
    response = client.get("/v1/user/info", params={"user_id": get_uid_from_auth(auth)})
    assert response.status_code == status.HTTP_200_OK
    return response.json()

def test_change_username():
    """
    This test creates a user, changes its name, and verifies everything is ok.
    """
    auth = create_quick_user()
    assert get_user_info(auth)["name"] != "testuser"

    response = client.post("/v1/user/change_name", params={
        "new_name": "testuser",
    }, headers={'Authorization': auth})

    assert response.status_code == status.HTTP_200_OK
    assert response.text == ""
    assert get_user_info(auth)["name"] == "testuser"

def test_change_username_with_no_session():
    response = client.post("/v1/user/change_name", params={
        "new_name": "this user shouldn't exist",
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    print(response.text)
    AuthenticationErrorResponse.model_validate_json(response.text)

def test_change_username_with_too_long_name():
    auth = create_quick_user()
    previous_name = get_user_info(auth)["name"]

    response = client.post("/v1/user/change_name", params={
        "new_name": "this is an extremely long username you could even say it isnt a username at all and is instead just a test",
    }, headers={'Authorization': auth})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert get_user_info(auth)["name"] == previous_name
    ErrorResponse.model_validate_json(response.text)

def test_change_username_with_non_alphanumeric_name():
    auth = create_quick_user()
    previous_name = get_user_info(auth)["name"]

    response = client.post("/v1/user/change_name", params={
        "new_name": "just a regular username++",
    }, headers={'Authorization': auth})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert get_user_info(auth)["name"] == previous_name
    ErrorResponse.model_validate_json(response.text)
