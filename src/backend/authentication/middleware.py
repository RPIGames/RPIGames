from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from db.models import User
from db.engine import get_session

security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)

# Dependecy, reads the Bearer token and returns the User model that it corresponds to
# Returns None if no authorization or if authorization failed
def is_logged_in (
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security_optional)],
) -> bool:
    if credentials == None:
        return False
    if not credentials.scheme == "Bearer":
        return False
    if len(credentials.credentials) == 0:
        return False
    return True

def force_authorization (
        credentials: HTTPAuthorizationCredentials = Depends(security),
        session: Session = Depends(get_session),
) -> User:
    if not credentials.scheme == "Bearer":
        raise HTTPException(status.HTTP_403_FORBIDDEN,
            {"detail": "Must have Bearer token."}
        )
    user = session.exec(select(User).where(User.secret == UUID(credentials.credentials))).first()
    if user == None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
            {"detail": "User token invalid or expired."}
        )
    return user
