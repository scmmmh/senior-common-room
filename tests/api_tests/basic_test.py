"""Basic connection test."""
import asyncio
import json
import pytest

from tornado.httpserver import HTTPServer
from tornado.web import Application
from tornado.websocket import websocket_connect, WebSocketClientConnection
from typing import Awaitable

from senior_common_room.models import create_engine, Base
from senior_common_room.servers.backend import create_application


config = {
    'core': {
        'title': 'Senior Common Room Test'
    },
    'database': {
        'dsn': 'sqlite+aiosqlite:///:memory:'
    },
    'mosquitto': '127.0.0.1'
}


@pytest.fixture
def app() -> Application:
    """Application fixture."""
    return create_application(config)


@pytest.fixture
def websocket(http_port: int) -> Awaitable[WebSocketClientConnection]:
    """Websocket connection fixture."""
    return websocket_connect(f'ws://localhost:{http_port}/api/websocket')


@pytest.fixture
def database() -> Awaitable:
    """Database fixture."""
    async def database_setup() -> None:
        async with create_engine(config['database']['dsn']).begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    return database_setup


@pytest.mark.gen_test(run_sync=False)
async def test_initial_authentication_required(http_server: HTTPServer, websocket: Awaitable,
                                               database: Awaitable) -> None:
    """Test that the initial authentication request is sent."""
    await database()
    conn = await websocket
    assert json.loads(await conn.read_message()) == {'type': 'authentication-required'}
    conn.close()
    await asyncio.sleep(2)
