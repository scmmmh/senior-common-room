"""Test configuration fixtures."""
import asyncio
import json
import pytest

from collections import namedtuple
from tornado.httpserver import HTTPServer
from tornado.web import Application
from tornado.websocket import WebSocketClientConnection, websocket_connect
from typing import Awaitable, Callable

from senior_common_room.models import Base, create_engine
from senior_common_room.servers.backend import create_application


CONFIG = {
    'database': {
        'dsn': 'sqlite+aiosqlite:///:memory:'
    }
}


@pytest.fixture
def app() -> Application:
    """Application fixture."""
    return create_application(CONFIG)


@pytest.fixture
def database() -> Awaitable:
    """Connect to the database, creating any needed database entries."""
    async def create() -> None:
        engine = create_engine(CONFIG['database']['dsn'])
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    return create


@pytest.fixture
def websocket(base_url: str) -> Awaitable[WebSocketClientConnection]:
    """Websocket fixture that creates a websocket."""
    return websocket_connect(base_url.replace('http', 'ws') + '/api/websocket')


ApiClient = namedtuple('ApiClient', ['expect_message', 'close'])


@pytest.fixture
def api_client(http_server: HTTPServer, websocket: Awaitable[WebSocketClientConnection]) -> \
        Awaitable[Callable[[], ApiClient]]:
    """Client for interacting with the websocket API."""
    async def connect() -> Awaitable[ApiClient]:
        """Connect to the API, returning the ."""
        conn = await websocket

        async def expect_message(msg: dict, timeout: int = 1) -> bool:
            """Wait for the given ``msg`` to arrive within the ``timeout``.

            :param msg: The message to expect
            :type msg: dict
            :param timeout: The timeout to wait for the message. Defaults to 1
            :type timeout: int
            """
            while True:
                try:
                    received_msg = json.loads(await asyncio.wait_for(conn.read_message(), timeout))
                    if received_msg == msg:
                        return True
                except asyncio.TimeoutError:
                    close()
                    assert False, f'Message {json.dumps(msg)} not received within {timeout} seconds'

        def close() -> None:
            """Close the connection."""
            conn.close()

        return ApiClient(**{
            'expect_message': expect_message,
            'close': close,
        })

    return connect
