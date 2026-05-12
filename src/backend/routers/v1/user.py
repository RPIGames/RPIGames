"""
This user router file contains endpoints relating to user creation and info fetching.
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, APIRouter, Response, status
from sqlmodel import Session

from db.models import User
from db.engine import get_session
from authentication.middleware import force_authorization, is_logged_in
from models.response import ErrorResponse, PrivateUserInfoResponse, UserTokenResponse, PublicUserInfoResponse

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

@router.post("/new")
def get_new_user_token(
        logged_in: Annotated[bool, Depends(is_logged_in)],
        session: Annotated[Session, Depends(get_session)],
        response: Response,
    ) -> UserTokenResponse | ErrorResponse:
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

@router.get("/info_self")
def get_user_info(
        user: Annotated[User, Depends(force_authorization)],
    ) -> PrivateUserInfoResponse:
    '''
    Gets user info. Since this returns private data, it requires the users authorization.
    '''
    return PrivateUserInfoResponse (
        id       = user.id,
        name     = user.name,
        leader   = user.leader,
        lobby_id = user.lobby_id,
    )

@router.get("/info")
def get_public_user_info (
        user_id: UUID,
        session: Annotated[Session, Depends(get_session)],
        response: Response,
    ) -> PublicUserInfoResponse | ErrorResponse:
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

    