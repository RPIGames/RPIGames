"""
This router file contains definitions for the /lobby endpoints
of the API.
"""

import random
from typing import Annotated

from cryptography.hazmat.primitives import constant_time
from fastapi import APIRouter, Depends, Response, status

from authentication.middleware import require_authorization
from games.registry import GAMES
from games_api.lobby import GLOBAL_LOBBY_MAP, Lobby, get_players_lobby
from games_api.player import Player
from games_api.private_maps import PLAYER_TO_LOBBY_MAP
from models.request import (
    LobbyJoinRequest,
    LobbyPassLeadershipRequest,
    MakeLobbyRequest,
)
from models.response import (
    AuthenticationErrorResponse,
    ErrorResponse,
    LobbyResponse,
    OkResponse,
)

router = APIRouter(
    prefix="/lobby",
    tags=["lobby"],
)


def mk_lobby_response_from_lobby(lobby: Lobby) -> LobbyResponse:
    """
    This helper function extracts the values needed to
    make a `LobbyResponse` from the `Lobby` passed into it.
    """
    return LobbyResponse(
        id=lobby._uuid,
        name=lobby.name,
        max_members=lobby.capacity,
        curr_members=len(lobby._players),
        needs_secret=lobby.secret is not None,
    )


@router.get("/all")
def get_all_lobbies() -> list[LobbyResponse]:
    """
    Gets all the currently available lobbies.
    """

    database_lobbies = GLOBAL_LOBBY_MAP.values()

    lobbies: list[LobbyResponse] = []
    for lobby in database_lobbies:
        lobbies.append(mk_lobby_response_from_lobby(lobby))

    return lobbies

@router.post(
    "/new",
    responses={
        status.HTTP_200_OK: {"model": LobbyResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": AuthenticationErrorResponse},
    },
)
async def make_lobby(
    player: Annotated[Player, Depends(require_authorization)],
    response: Response,
    body: MakeLobbyRequest,
):
    """
    Creates a lobby. Needs an authorization from a user.

    The lobby will be initialized to contain the user, which gains leadership of the party.
    """

    if PLAYER_TO_LOBBY_MAP.get(player.uuid) is not None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ErrorResponse(error="You are already in a lobby!")

    if body.name is None:
        body.name = f"Unnamed group {random.randint(1, 1000)}"

    if body.game_type_id not in GAMES:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ErrorResponse(error=f"{body.game_type_id} is not a valid game_id")

    created_lobby = Lobby(
        game_name=body.game_type_id,
        game_settings=body.game_config,
        leader=Player(player.uuid),
        lobby_size=body.game_capacity,
        name=body.name,
        secret=body.secret
    )
    return mk_lobby_response_from_lobby(created_lobby)


@router.post(
    "/join",
    responses={
        status.HTTP_200_OK: {"model": OkResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": AuthenticationErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
)
async def join_lobby(
    player: Annotated[Player, Depends(require_authorization)],
    response: Response,
    body: LobbyJoinRequest,
):
    """
    Joins a lobby specified by lobby_id.

    If the lobby is a secret lobby, pass the lobby_secret parameter with the password to the lobby.
    """

    lobby_id = PLAYER_TO_LOBBY_MAP.get(player.uuid)

    if lobby_id is not None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        if lobby_id == body.lobby_id:
            return ErrorResponse(
                error="You are already in the lobby you are trying to join."
            )
        else:
            return ErrorResponse(
                error="You are already in a lobby! Leave your current lobby to join another one."
            )

    lobby = GLOBAL_LOBBY_MAP.get(body.lobby_id)
    if lobby is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorResponse(error="The lobby you are trying to join does not exist.")

    # check to see if the lobby is public or private, and check that the lobby secret matches

    if lobby.secret is None:
        if body.lobby_secret is not None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return ErrorResponse(
                error="The lobby you are trying to join is not private and thus does not require a password."
            )
        else:
            # no lobby secret needed!
            pass
    else:
        if body.lobby_secret is None:
            response.status_code = status.HTTP_403_FORBIDDEN
            return ErrorResponse(
                error="The lobby you are trying to join is private and requires a passphrase to access."
            )
        else:
            # lobby_secret is required. check with constant-time equality
            if not constant_time.bytes_eq(body.lobby_secret.encode(), lobby.secret.encode()):
                response.status_code = status.HTTP_403_FORBIDDEN
                return ErrorResponse(error="The passphrase was incorrect.")

    if lobby.capacity <= len(lobby._players):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ErrorResponse(error="The lobby you are trying to join is full.")

    try:
        await lobby.add_player(player)
    except ValueError as err:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ErrorResponse(error=str(err))

    return OkResponse()


@router.post(
    "/leave",
    responses={
        status.HTTP_200_OK: {"model": OkResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": AuthenticationErrorResponse},
    },
)
async def leave_lobby(
    player: Annotated[Player, Depends(require_authorization)],
    response: Response,
):
    """
    Leaves the lobby you are currently in.
    """

    lobby_id = PLAYER_TO_LOBBY_MAP.get(player.uuid)

    if lobby_id is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ErrorResponse(error="You aren't currently in a lobby.")

    lobby = GLOBAL_LOBBY_MAP[lobby_id]

    await lobby.remove_player(Player(player.uuid))

    return OkResponse()


@router.post(
    "/leadership/grant",
    responses={
        status.HTTP_200_OK: {"model": OkResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
    },
)
def pass_leadership(
    user: Annotated[Player, Depends(require_authorization)],
    response: Response,
    body: LobbyPassLeadershipRequest,
):
    """
    This method gives the leadership role to someone else in your session.

    The grant_to_user_id expects a valid user id that is in your same lobby.
    """

    lobby = get_players_lobby(user)

    if lobby is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ErrorResponse(error="You aren't currently in a lobby.")

    if lobby.leader != user:
        response.status_code = status.HTTP_403_FORBIDDEN
        return ErrorResponse(
            error="You aren't currently a leader, and thus cannot grant leadership to someone else."
        )

    try:
        new_leader = Player(body.grantee_id)
    except ValueError:
        new_leader = None

    if new_leader is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ErrorResponse(
            error="The user that you are trying to pass leadership to is not in your lobby."
        )

    if get_players_lobby(new_leader) != lobby:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ErrorResponse(
            error="The user that you are trying to pass leadership to is not in your lobby."
        )

    lobby.leader = new_leader

    return OkResponse()
