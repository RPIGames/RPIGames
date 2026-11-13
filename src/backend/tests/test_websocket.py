import concurrent.futures

import pytest

from models.websocket import ClientAuthenticationMessage

from .helper import GARBAGE_TOKENS, client, create_quick_user


@pytest.mark.asyncio
async def websocket_timeout_recieve(websocket, timeout: float = 0.5) -> str | None:
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    future = executor.submit(websocket.receive_text)

    try:
        return future.result(timeout=timeout)
    except concurrent.futures.TimeoutError:
        return None
    finally:
        executor.shutdown(wait=False, cancel_futures=True)


@pytest.mark.asyncio
async def test_websocket_authenticate():
    user = create_quick_user()
    with client.websocket_connect("/v1/websocket/") as websocket:
        websocket.send_text(ClientAuthenticationMessage(token=user).model_dump_json())
        _data = await websocket_timeout_recieve(websocket, 0.5)
        #assert data is not None
        #ServerConnectionStatusMessage.model_validate_json(data)


@pytest.mark.asyncio
async def test_websocket_bogus_authenticate_token():
    with client.websocket_connect("/v1/websocket/") as websocket:
        for header in GARBAGE_TOKENS:
            websocket.send_text(
                ClientAuthenticationMessage(token=header).model_dump_json()
            )
            _data = await websocket_timeout_recieve(websocket, 0.5)
            #assert data is not None
            #ServerConnectionStatusMessage.model_validate_json(data)


@pytest.mark.asyncio
async def test_websocket_authenticate_garbage():
    with client.websocket_connect("/v1/websocket/") as websocket:
        for token in GARBAGE_TOKENS:
            websocket.send_text(token)
            data = await websocket_timeout_recieve(websocket, 0.5)
            assert data is None
