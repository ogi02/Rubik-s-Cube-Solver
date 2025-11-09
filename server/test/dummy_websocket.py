# Python imports
from typing import Optional

from fastapi import WebSocket


async def dummy_receive() -> dict:
    """
    A dummy receive function for the DummyWebSocket
    """

    return {"type": "websocket.connect"}


async def dummy_send(data) -> None:
    """
    A dummy send function for the DummyWebSocket

    :param data: The data to send
    """

    pass


class DummyWebSocket(WebSocket):
    """
    A minimal websocket stub that records sent json payloads.
    """

    def __init__(self) -> None:
        """
        Initializes the DummyWebSocket.
        """

        scope = {
            "type": "websocket",
            "asgi": {"version": "3.0"},
            "scheme": "ws",
            "path": "/",
            "headers": [],
            "query_string": b"",
            "client": ("testclient", 12345),
            "server": ("testserver", 80),
            "subprotocols": [],
        }
        super().__init__(scope=scope, receive=dummy_receive, send=dummy_send)
        self.sent: list = []
        self.closed: bool = False
        self.closed_code: Optional[int] = None
        self.closed_reason: Optional[str] = None

    async def send_json(self, data, mode: str = "test", **kwargs) -> None:
        """
        Records the JSON data.

        :param data: The JSON data to record.
        :param mode: The mode of sending (default is "test").
        :param kwargs: Additional keyword arguments.
        """

        self.sent.append(data)

    async def close(self, code: int = 1000, reason: Optional[str] = None) -> None:
        """
        Records the closure of the websocket.

        :param code: The closure code.
        :param reason: The reason for closure.
        """

        self.closed = True
        self.closed_code = code
        self.closed_reason = reason
