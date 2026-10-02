"""
This file contains tests for creating users,
as well as testing when users fail to be created
(for example, a bogus header)
"""

from fastapi import status
from fastapi.testclient import TestClient

from .helper import create_quick_user, get_user_info
from main import app
from models.response import AuthenticationErrorResponse, ErrorResponse

client = TestClient(app)

def test_change_username():
    """
    This test creates a user, changes its name, and verifies everything is ok.
    """
    auth = create_quick_user(client)
    assert get_user_info(auth, client)["name"] != "testuser"

    response = client.post(
        "/v1/user/change_name",
        params={
            "new_name": "testuser",
        },
        headers={"Authorization": auth},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.text == ""
    assert get_user_info(auth, client)["name"] == "testuser"


def test_change_username_with_no_session():
    response = client.post(
        "/v1/user/change_name",
        params={
            "new_name": "this user shouldn't exist",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    print(response.text)
    AuthenticationErrorResponse.model_validate_json(response.text)


def test_change_username_with_too_long_name():
    auth = create_quick_user(client)
    previous_name = get_user_info(auth, client)["name"]

    response = client.post(
        "/v1/user/change_name",
        params={
            "new_name": "this is an extremely long username you could even say it isn't a username at all and is instead just a test.",
        },
        headers={"Authorization": auth},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert get_user_info(auth, client)["name"] == previous_name
    ErrorResponse.model_validate_json(response.text)


def test_change_username_with_non_alphanumeric_name():
    auth = create_quick_user(client)
    previous_name = get_user_info(auth, client)["name"]

    response = client.post(
        "/v1/user/change_name",
        params={
            "new_name": "just a regular username++",
        },
        headers={"Authorization": auth},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert get_user_info(auth, client)["name"] == previous_name
    ErrorResponse.model_validate_json(response.text)
