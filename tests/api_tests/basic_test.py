import asyncio
import json
import pytest

from tornado.websocket import websocket_connect

from senior_common_room.server import create_application


config = {
    'core': {
        'title': 'Senior Common Room Test'
    },
    'database': {
        'dsn': 'postgresql+asyncpg://postgres:devPWD@localhost:5432/postgres'
    },
    'mosquitto': '127.0.0.1'
}


@pytest.fixture
def app():
    return create_application(config)


@pytest.fixture
def websocket(http_port):
    return websocket_connect(f'ws://localhost:{http_port}/api')


@pytest.mark.gen_test(run_sync=False)
async def test_initial_authentication_required(http_server, websocket):
    conn = await websocket
    assert json.loads(await conn.read_message()) == {'type': 'authentication-required'}
    conn.close()
    await asyncio.sleep(2)
