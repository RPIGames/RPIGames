from fastapi import APIRouter

from .v1 import lobby, user, websocket

router = APIRouter()

router.include_router(user.router)
router.include_router(lobby.router)
router.include_router(websocket.router)
