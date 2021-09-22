"""Test configuration fixtures."""
import asyncio
import json
import pytest

from collections import namedtuple
from tornado.httpserver import HTTPServer
from tornado.web import Application
from tornado.websocket import WebSocketClientConnection, websocket_connect
from typing import Awaitable, Callable, Union, List

from senior_common_room.models import Base, User, create_engine, create_sessionmaker
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
    async def create(objects: Union[List[dict], None] = None) -> None:
        async with create_engine(CONFIG['database']['dsn']).begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            if objects:
                async with create_sessionmaker(engine=conn)() as session:
                    async with session.begin():
                        for data in objects:
                            if data['type'] == 'users':
                                obj = User.from_jsonapi(data)
                                session.add(obj)
    return create


@pytest.fixture
def websocket(base_url: str) -> Awaitable[WebSocketClientConnection]:
    """Websocket fixture that creates a websocket."""
    return websocket_connect(base_url.replace('http', 'ws') + '/api/websocket')


ApiClient = namedtuple('ApiClient', ['expect_message', 'send_message', 'close'])


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

        async def send_message(msg: dict) -> None:
            """Send the given ``msg``.

            :param msg: The message to send to the server
            :type msg: dict
            """
            conn.write_message(json.dumps(msg))

        def close() -> None:
            """Close the connection."""
            conn.close()

        return ApiClient(**{
            'expect_message': expect_message,
            'send_message': send_message,
            'close': close,
        })

    return connect
