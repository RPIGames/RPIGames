"""
This file contains the Game sub-API for the Game API.
Everything that shouldn't exist in any other sub-API
lives here.
"""

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID


def schedule(
    delay_minutes: float,
    function: Callable[..., Awaitable[Any]],
    *args: Any,
    **kwargs: Any,
) -> asyncio.Task[Any]:
    async def run() -> Any:
        await asyncio.sleep(delay_minutes * 60)
        return await function(*args, **kwargs)

    return asyncio.create_task(run())


class Game:
    def __init__(self, lobby_id: UUID):
        self._lobby_id = lobby_id

    #give utc time when end, send update when timer is changed 
    #send timer to user each timer ahas unique identifier, countdown, send timer name and end on completion 
    def make_timer(
        self,
        timer_seconds: float,
        timer_name: str = "Untitled Timer",
        disappear_on_completion: bool = True,
    ) -> None:
        raise NotImplementedError

    #add scoreboard
    #takes in a sorted array that this then sends to front end.
    #takes in an amount of scores that are being stored
    #also takes the which score it is 

