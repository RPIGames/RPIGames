"""
This user router file contains endpoints relating to user creation and info fetching.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from authentication.middleware import parse_credentials, require_authorization
from db.engine import get_session
from db.models import User
from games_api.lobby import GLOBAL_LOBBY_MAP, get_players_lobby
from games_api.player import Player
from games_api.private_maps import PLAYER_TO_LOBBY_MAP
from models.response import (
    AuthenticationErrorResponse,
    ErrorResponse,
    PrivateUserInfoResponse,
    PublicUserInfoResponse,
    UserTokenResponse,
)

router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@router.post(
    "/new",
    responses={
        status.HTTP_200_OK: {"model": UserTokenResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": AuthenticationErrorResponse},
    },
)
def get_new_user_token(
    credentials: Annotated[tuple[str, str] | None, Depends(parse_credentials)],
    session: Annotated[Session, Depends(get_session)],
    response: Response,
):
    """
    Creates a new user token.
    """

    if credentials is not None:
        response.status_code = 400
        return ErrorResponse(error="You are already sending a valid user token.")

    new_user = User()
    session.add(new_user)
    session.commit()

    return UserTokenResponse(id=new_user.id, secret=new_user.secret)


@router.get(
    "/info_self",
    responses={
        status.HTTP_200_OK: {"model": PrivateUserInfoResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": AuthenticationErrorResponse},
    },
)
def get_user_info(
    user: Annotated[Player, Depends(require_authorization)],
):
    """
    Gets user info. Since this returns private data, it requires the user's authorization.
    """

    lobby_id = PLAYER_TO_LOBBY_MAP.get(user.uuid)

    leader = False

    if lobby_id is not None:
        lobby = GLOBAL_LOBBY_MAP.get(lobby_id)
        if lobby is not None:
            leader = lobby.leader == user

    return PrivateUserInfoResponse(
        id=user.uuid,
        name=user.get_name(),
        leader=leader,
        lobby_id=lobby_id,
    )


@router.get(
    "/info",
    responses={
        status.HTTP_200_OK: {"model": PublicUserInfoResponse},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
)
def get_public_user_info(
    user_id: UUID,
    response: Response,
):
    """
    Gets public user info. Requires a user_id, a UUID that uniquely defines the user.
    """

    player = None
    try:
        player = Player(user_id)
    except ValueError:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorResponse(error="User not found.")

    leader = False
    lobby = get_players_lobby(player)
    lobby_id = None
    if lobby is not None:
        lobby_id = lobby._uuid
        if lobby.leader == player:
            leader = True

    return PublicUserInfoResponse(
        id=player.uuid,
        name=player.get_name(),
        leader=leader,
        lobby_id=lobby_id,
    )


@router.post(
    "/change_name",
    responses={
        status.HTTP_200_OK: {},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": AuthenticationErrorResponse},
    },
)
def rename_self(
    new_name: str,
    player: Annotated[Player, Depends(require_authorization)],
    session: Annotated[Session, Depends(get_session)],
    response: Response,
):
    """
    Changes your username to new_name. There are some restrictions though:

    - Usernames must be greater than or equal to 3 characters long.
    - Usernames must be less than or equal to 50 characters long.
    - Usernames must be alphanumeric (+ spaces)
    """

    if len(new_name) < 3:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ErrorResponse(error="new_name is too short")

    if len(new_name) > 50:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ErrorResponse(error="new_name is too long")

    new_name = new_name.strip()
    for segment in new_name.split(" "):
        if not segment.isalnum():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return ErrorResponse(error="new_name is not alphanumeric")

    user = session.get(User, player.uuid)

    assert user is not None

    user.name = new_name

    session.commit()

    return Response(status_code=status.HTTP_200_OK)


@router.delete(
    "/sign_out",
    responses={
        status.HTTP_200_OK: {},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": AuthenticationErrorResponse},
    },
)
def sign_out(
    player: Annotated[Player, Depends(require_authorization)],
    session: Annotated[Session, Depends(get_session)],
    response: Response,
):
    """
    Signs out a user by setting out the name to nothing and uuid

    -User must not be in a lobby
    """

    if get_players_lobby(player) is not None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ErrorResponse(error="You are currently in a lobby.")

    # delete user row
    user = session.get(User, player.uuid)

    if user is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ErrorResponse(error="Your user seems to not exist anymore.")
    session.delete(user)
    session.commit()

    return Response(status_code=status.HTTP_200_OK)
