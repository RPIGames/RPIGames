from fastapi import APIRouter

from .v1 import user

router = APIRouter()

router.include_router(user.router)
