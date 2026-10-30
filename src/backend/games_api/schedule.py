
import asyncio
from collections.abc import Awaitable, Callable
from typing import Any


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
