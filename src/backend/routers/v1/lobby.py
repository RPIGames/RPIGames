"""
This router file contains definitions for the /lobby endpoints
of the API.
"""

import random
from typing import Annotated, Optional
from uuid import UUID
from cryptography.hazmat.primitives import constant_time

from fastapi import Depends, APIRouter, HTTPException, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import Session, select

from db.models import User, Lobby
from db.engine import get_session
from authentication.middleware import force_authorization, is_logged_in
from models.response import AuthenticationErrorResponse, OkResponse, ErrorResponse, LobbyResponse

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
        id=lobby.id,
        name=lobby.name,
        max_members=lobby.max_size,
        curr_members=len(lobby.users),
    )

@router.get("/all")
def get_all_lobbies(
        session: Annotated[Session, Depends(get_session)],
    ) -> list[LobbyResponse]:
    '''
    Gets all the currently available lobbies.
    '''
    
    database_lobbies = session.exec(select(Lobby)).all()
    
    lobbies: list[LobbyResponse] = []
    for lobby in database_lobbies:
        lobbies.append(mk_lobby_response_from_lobby(lobby))

    return lobbies



@router.post("/new", responses={
    status.HTTP_200_OK: {"model": LobbyResponse},
    status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
    status.HTTP_401_UNAUTHORIZED: {"model": AuthenticationErrorResponse},
})
def make_lobby(
        user: Annotated[User, Depends(force_authorization)],
        session: Annotated[Session, Depends(get_session)],
        response: Response,
        name: Optional[str] = None,
        secret: Optional[str] = None,
    ):
    '''
    Creates a lobby. Needs an authorization from a user.

    The lobby will be initialized to contain the user, which gains leadership of the party.
    '''

    if user.lobby != None:
        response = status.HTTP_400_BAD_REQUEST
        return ErrorResponse(error="You are already in a lobby!")

    if name == None:
        name = f"Unnamed group {random.randint(1, 1000)}"

    created_lobby = Lobby(name=name, max_size=8, secret=secret)
    session.add(created_lobby)

    user.lobby = created_lobby
    user.leader = True

    session.commit()

    return mk_lobby_response_from_lobby(created_lobby)



@router.post("/join", responses={
    status.HTTP_200_OK: {"model": OkResponse},
    status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
    status.HTTP_401_UNAUTHORIZED: {"model": AuthenticationErrorResponse},
    status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
    status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
})
def join_lobby(
        user: Annotated[User, Depends(force_authorization)],
        session: Annotated[Session, Depends(get_session)],
        response: Response,
        lobby_id: UUID,
        lobby_secret: Optional[str] = None,
    ):
    '''
    Joins a lobby specified by lobby_id.

    If the lobby is a secret lobby, pass the lobby_secret parameter with the password to the lobby.
    '''

    if user.lobby != None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        if user.lobby_id == lobby_id:
            return ErrorResponse(error="You are already in the lobby you are trying to join.")
        else:
            return ErrorResponse(error="You are already in a lobby! Leave your current lobby to join another one.")

    assert user.leader == False
    
    lobby = session.get(Lobby, lobby_id)
    if lobby == None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorResponse(error="The lobby you are trying to join does not exist.")
    
    # check to see if the lobby is public or private, and check that the lobby secret matches

    if lobby.secret == None:
        if lobby_secret != None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return ErrorResponse(error="The lobby you are trying to join is not private and thus does not require a password.")
        else:
            # no lobby secret needed!
            pass
    else:
        if lobby_secret == None:
            response.status_code = status.HTTP_403_FORBIDDEN
            return ErrorResponse(error="The lobby you are trying to join is private and requires a passphrase to access.")
        else:
            # lobby_secret is required. check with constant-time equality
            if not constant_time.bytes_eq(lobby_secret.encode(), lobby.secret.encode()):
                response.status_code = status.HTTP_403_FORBIDDEN
                return ErrorResponse(error="The passphrase was incorrect.")

    if lobby.max_size <= len(lobby.users):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ErrorResponse(error="The lobby you are trying to join is full.")

    user.lobby = lobby

    session.commit()

    return OkResponse()


@router.post("/leave", responses={
    status.HTTP_200_OK: {"model": OkResponse},
    status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
    status.HTTP_401_UNAUTHORIZED: {"model": AuthenticationErrorResponse},
})
def leave_lobby(
        user: Annotated[User, Depends(force_authorization)],
        session: Annotated[Session, Depends(get_session)],
        response: Response,
    ):
    '''
    Leaves the lobby you are currently in.
    '''

    if user.lobby == None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ErrorResponse(error="You aren't currently in a lobby.")

    lobby = user.lobby
    user.lobby = None

    if user.leader:
        user.leader = False
        if len(lobby.users) == 0:
            # delete the lobby
            session.delete(lobby)
        else:
            # if there are no other leaders in the group, reassign leadership to random user
            leader_exists = False
            for group_member in lobby.users:
                if group_member.leader:
                    leader_exists = True
                    break
            if not leader_exists:
                random.choice(lobby.users).leader = True
    
    session.commit()

    return OkResponse()

@router.post("/leadership/grant", responses={
    status.HTTP_200_OK: {"model": OkResponse},
    status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
    status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
})

def pass_leadership(
        grantee_id: UUID,
        user: Annotated[User, Depends(force_authorization)],
        session: Annotated[Session, Depends(get_session)],
        response: Response,
    ):
    """
    This method gives the leadership role to someone else in your session.
    
    The grant_to_user_id expects a valid user id that is in your same lobby.
    """

    if user.lobby == None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ErrorResponse(error="You aren't currently in a lobby.")
    
    if user.leader == False:
        response.status_code = status.HTTP_403_FORBIDDEN
        return ErrorResponse(error="You aren't currently a leader, and thus cannot grant leadership to someone else.")
    
    new_leader = session.get(User, grantee_id)

    if new_leader == None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ErrorResponse(error="The user that you are trying to pass leadership to is not in your lobby.")

    if new_leader.lobby != user.lobby:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ErrorResponse(error="The user that you are trying to pass leadership to is not in your lobby.")

    user.leader = False
    new_leader.leader = True

    session.commit()

    return OkResponse()





