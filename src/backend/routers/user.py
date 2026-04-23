from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session

from db.models import User
from db.engine import get_session
from authentication.middleware import force_authorization, is_logged_in

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

@router.post("/new")
def get_new_user_token(
        logged_in: Annotated[bool, Depends(is_logged_in)],
        session: Session = Depends(get_session),
    ) -> JSONResponse:
    if logged_in:
        raise HTTPException(status_code=400, detail="You are already sending a valid user token")
    new_user = User()
    session.add(new_user)
    session.commit()
    return {
        "id": new_user.id,
        "secret": new_user.secret,
    }

@router.get("/info")
def get_user_info(
        user: Annotated[User, Depends(force_authorization)],
    ) -> User:
    return user