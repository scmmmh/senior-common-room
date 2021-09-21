"""Tests for the authorisation functions."""
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
