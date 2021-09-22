"""Tests for the authorisation functions."""
import asyncio
import pytest

from typing import Callable, Awaitable

from .conftest import ApiClient


@pytest.mark.gen_test()
async def test_initial_authorisation_request(database: Awaitable,
                                             api_client: Awaitable[Callable[[], ApiClient]]) -> None:
    """Test that the initial authorisation request message is received."""
    await database()
    client = await api_client()
    assert await client.expect_message({'type': 'authentication-required'})
    client.close()
    await asyncio.sleep(0.001)


@pytest.mark.gen_test()
async def test_token_login_success(database: Awaitable, api_client: Awaitable[Callable[[], ApiClient]]) -> None:
    """Test that a valid login token works."""
    await database(({
        'type': 'users',
        'id': '1',
        'attributes': {
            'name': 'Test User 1',
            'email': 'test1@example.com',
            'token': 'abc123',
            'status': 'active',
        }},))
    client = await api_client()
    assert await client.expect_message({'type': 'authentication-required'})
    await client.send_message({
        'type': 'authenticate',
        'payload': {
            'email': 'test1@example.com',
            'token': 'abc123'
        }
    })
    assert await client.expect_message({'type': 'authenticated'})
    client.close()
    await asyncio.sleep(0.001)


@pytest.mark.gen_test()
async def test_token_login_failed_1(database: Awaitable, api_client: Awaitable[Callable[[], ApiClient]]) -> None:
    """Test that an invalid login token fails."""
    await database(({
        'type': 'users',
        'id': '1',
        'attributes': {
            'name': 'Test User 1',
            'email': 'test1@example.com',
            'token': 'abc123',
            'status': 'active',
        }},))
    client = await api_client()
    assert await client.expect_message({'type': 'authentication-required'})
    await client.send_message({
        'type': 'authenticate',
        'payload': {
            'email': 'test2@example.com',
            'token': 'abc123'
        }
    })
    assert await client.expect_message({'type': 'authentication-failed'})
    client.close()
    await asyncio.sleep(0.001)


@pytest.mark.gen_test()
async def test_token_login_failed_2(database: Awaitable, api_client: Awaitable[Callable[[], ApiClient]]) -> None:
    """Test that an invalid e-mail address fails."""
    await database(({
        'type': 'users',
        'id': '1',
        'attributes': {
            'name': 'Test User 1',
            'email': 'test1@example.com',
            'token': 'abc123',
            'status': 'active',
        }},))
    client = await api_client()
    assert await client.expect_message({'type': 'authentication-required'})
    await client.send_message({
        'type': 'authenticate',
        'payload': {
            'email': 'test1@example.com',
            'token': '123abc'
        }
    })
    assert await client.expect_message({'type': 'authentication-failed'})
    client.close()
    await asyncio.sleep(0.001)


@pytest.mark.gen_test()
async def test_token_login_failed_3(database: Awaitable, api_client: Awaitable[Callable[[], ApiClient]]) -> None:
    """Test that a blocked user authentication fails."""
    await database(({
        'type': 'users',
        'id': '1',
        'attributes': {
            'name': 'Test User 1',
            'email': 'test1@example.com',
            'token': 'abc123',
            'status': 'blocked',
        }},))
    client = await api_client()
    assert await client.expect_message({'type': 'authentication-required'})
    await client.send_message({
        'type': 'authenticate',
        'payload': {
            'email': 'test1@example.com',
            'token': 'abc123'
        }
    })
    assert await client.expect_message({'type': 'authentication-failed'})
    client.close()
    await asyncio.sleep(0.001)
