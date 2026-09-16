from fastapi import APIRouter

from .v1 import lobby, user

router = APIRouter()

router.include_router(user.router)
router.include_router(lobby.router)
