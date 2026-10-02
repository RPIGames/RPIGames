from .helper import GARBAGE_AUTH_HEADERS, client, create_quick_user


def test_websocket_authenticate():
    user = create_quick_user()
    with client.websocket_connect("/v1/websocket/") as websocket:
        websocket.send_text(user)
        data = websocket.receive_text()
        assert data == "Authentication Successful"

def test_websocket_authenticate_garbage():
    with client.websocket_connect("/v1/websocket/") as websocket:
        for header in GARBAGE_AUTH_HEADERS:
            websocket.send_text(next(iter(header.values())))
            data = websocket.receive_text()
            assert data == "We fed your credentials to THE SNAKE."

def test_websocket_message_authenticated():
    user = create_quick_user()
    with client.websocket_connect("/v1/websocket/") as websocket:
        websocket.send_text(user)
        _ = websocket.receive_text()
        test_messages = [
            "Hello",
            "thing",
            "why is this happening",
            "heeeeeeeeellllllllllllllllllllllp",
            "you like jazzzz?"
        ]
        for message in test_messages:
            websocket.send_text(message)
            data = websocket.receive_text()
            assert data == message
