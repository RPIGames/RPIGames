import concurrent.futures

import pytest

from models.websocket import ClientAuthenticationMessage

from .helper import GARBAGE_TOKENS, client, create_quick_user

"""
Client sends stuff: 
    connection established
    authentication successful
    authentication failed
    already authenticated
    request timers
    request scoreboards
    sent chat message
        to room in: check self and other
        to room not in: check self and other (in that room)
    send location
    send button press (not implemented yet)
    fetch button args (not implemented yet)
    
Server Call:
    authenticated (true and false cases)
    update timers
    delete timer
    update scoreboards
    delete scoreboards
    send message
    update chatroom
    update markers
    delete markers
    update buttons
    delete buttons
    send notification
"""

@pytest.mark.asyncio
async def websocket_timeout_receive(websocket, timeout: float = 0.5) -> str | None:
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
        _data = await websocket_timeout_receive(websocket, 0.5)
        #assert data is not None
        #ServerConnectionStatusMessage.model_validate_json(data)


@pytest.mark.asyncio
async def test_websocket_bogus_authenticate_token():
    with client.websocket_connect("/v1/websocket/") as websocket:
        for header in GARBAGE_TOKENS:
            websocket.send_text(
                ClientAuthenticationMessage(token=header).model_dump_json()
            )
            _data = await websocket_timeout_receive(websocket, 0.5)
            #assert data is not None
            #ServerConnectionStatusMessage.model_validate_json(data)


@pytest.mark.asyncio
async def test_websocket_authenticate_garbage():
    with client.websocket_connect("/v1/websocket/") as websocket:
        for token in GARBAGE_TOKENS:
            websocket.send_text(token)
            data = await websocket_timeout_receive(websocket, 0.5)
            assert data is None
