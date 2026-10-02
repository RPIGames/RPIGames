"""
This file contains tests for creating users,
as well as testing when users fail to be created
(for example, a bogus header)
"""

from fastapi import status

from models.response import AuthenticationErrorResponse, ErrorResponse

from .helper import client, create_quick_user, get_uid_from_auth, get_user_info
from .test_lobby import create_quick_lobby


def test_change_username():
    """
    This test creates a user, changes its name, and verifies everything is ok.
    """
    auth = create_quick_user()
    assert get_user_info(auth)["name"] != "testuser"

    response = client.post(
        "/v1/user/change_name",
        params={
            "new_name": "testuser",
        },
        headers={"Authorization": auth},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.text == ""
    assert get_user_info(auth)["name"] == "testuser"


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
    auth = create_quick_user()
    previous_name = get_user_info(auth)["name"]

    response = client.post(
        "/v1/user/change_name",
        params={
            "new_name": "this is an extremely long username you could even say it isn't a username at all and is instead just a test.",
        },
        headers={"Authorization": auth},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert get_user_info(auth)["name"] == previous_name
    ErrorResponse.model_validate_json(response.text)


def test_change_username_with_non_alphanumeric_name():
    auth = create_quick_user()
    previous_name = get_user_info(auth)["name"]

    response = client.post(
        "/v1/user/change_name",
        params={
            "new_name": "just a regular username++",
        },
        headers={"Authorization": auth},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert get_user_info(auth)["name"] == previous_name
    ErrorResponse.model_validate_json(response.text)


def test_user_logout():
    """
    This test creates a user, signs it out, and verifies that it was deleted.
    """
    auth = create_quick_user()
    response = client.delete(
        "/v1/user/sign_out",
        headers={"Authorization": auth},
    )
    test_response = client.get(
        "/v1/user/info", params={"user_id": str(get_uid_from_auth(auth))}
    )
    assert response.status_code == status.HTTP_200_OK
    assert test_response.status_code == status.HTTP_404_NOT_FOUND


def test_user_no_auth_logout():
    """
    This test creates a user, tries to sign it out without authenticating, and verifies that it the request fails and that the user wasn't deleted.
    """
    auth = create_quick_user()
    previous_name = get_user_info(auth)["name"]
    previous_id = get_user_info(auth)["id"]
    response = client.delete(
        "/v1/user/sign_out",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert previous_name == get_user_info(auth)["name"]
    assert previous_id == get_user_info(auth)["id"]


def test_user_in_lobby_logout():
    """
    This test creates a user, attempts to sign it out while the user is in a lobby, verifies that it fails and that it still exists.
    """
    auth = create_quick_user()
    create_quick_lobby(auth)
    previous_name = get_user_info(auth)["name"]
    previous_id = get_user_info(auth)["id"]
    response = client.delete(
        "/v1/user/sign_out",
        headers={"Authorization": auth},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert previous_name == get_user_info(auth)["name"]
    assert previous_id == get_user_info(auth)["id"]
