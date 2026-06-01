"""
This user router file contains endpoints relating to user creation and info fetching.
"""

from types import NoneType
from typing import Annotated
from uuid import UUID

from fastapi import Depends, APIRouter, Response, status
from sqlmodel import Session

from db.models import User
from db.engine import get_session
from authentication.middleware import force_authorization, is_logged_in
from models.response import AuthenticationErrorResponse, ErrorResponse, PrivateUserInfoResponse, UserTokenResponse, PublicUserInfoResponse

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

@router.post("/new", responses={
    status.HTTP_200_OK: {"model": UserTokenResponse},
    status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
    status.HTTP_401_UNAUTHORIZED: {"model": AuthenticationErrorResponse},
})
def get_new_user_token(
        logged_in: Annotated[bool, Depends(is_logged_in)],
        session: Annotated[Session, Depends(get_session)],
        response: Response,
    ):
    '''
    Creates a new user token.
    '''

    if logged_in:
        response.status_code = 400
        return ErrorResponse(error = "You are already sending a valid user token.")

    new_user = User()
    session.add(new_user)
    session.commit()

    return UserTokenResponse(
        id = new_user.id,
        secret = new_user.secret
    )

@router.get("/info_self", responses={
    status.HTTP_200_OK: {"model": PrivateUserInfoResponse},
    status.HTTP_401_UNAUTHORIZED: {"model": AuthenticationErrorResponse},
})
def get_user_info(
        user: Annotated[User, Depends(force_authorization)],
    ):
    '''
    Gets user info. Since this returns private data, it requires the users authorization.
    '''

    return PrivateUserInfoResponse (
        id       = user.id,
        name     = user.name,
        leader   = user.leader,
        lobby_id = user.lobby_id,
    )

@router.get("/info", responses={
    status.HTTP_200_OK: {"model": PublicUserInfoResponse},
    status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
})
def get_public_user_info (
        user_id: UUID,
        session: Annotated[Session, Depends(get_session)],
        response: Response,
    ):
    '''
    Gets public user info. Requires a user_id, a UUID that uniquely defines the user.
    '''

    user = session.get(User, user_id)
    if user == None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorResponse(error = "User not found.")

    return PublicUserInfoResponse (
        id       = user.id,
        name     = user.name,
        leader   = user.leader,
        lobby_id = user.lobby_id,
    )

@router.post("/change_name", responses={
    status.HTTP_200_OK: {},
    status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
    status.HTTP_401_UNAUTHORIZED: {"model": AuthenticationErrorResponse},
})
def rename_self (
        new_name: str,
        user: Annotated[User, Depends(force_authorization)],
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
        if not new_name.isalnum():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return ErrorResponse(error="new_name is not alphanumeric")
    
    user.name = new_name

    session.commit()

    return Response(status_code=status.HTTP_200_OK)
