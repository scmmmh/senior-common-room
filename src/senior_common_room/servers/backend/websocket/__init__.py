"""Websocket handler."""
import asyncio
import json

from tornado import websocket

from .user import UserMixin
from senior_common_room.models import create_sessionmaker


mixins = ['user']
open_mixins = [f'{mixin}_on_open' for mixin in mixins]
message_mixins = [f'{mixin}_on_message' for mixin in mixins]
close_mixins = [f'{mixin}_on_close' for mixin in mixins]


class WebsocketHandler(websocket.WebSocketHandler, UserMixin):
    """Handler for the main websocket API."""

    def initialize(self, config: dict) -> None:  # noqa: ANN101
        """Initialise the handler."""
        self.config = config
        self.Session = create_sessionmaker(dsn=config['database']['dsn'])

    async def open(self) -> None:  # noqa: ANN101
        """Handle opening the connection and calls any on_open mixins."""
        for mixin in open_mixins:
            if hasattr(self, mixin):
                await getattr(self, mixin)()

    async def on_message(self, data: str) -> None:  # noqa: ANN101
        """Handle opening the connection and calls any on_message mixins."""
        msg = json.loads(data)
        for mixin in message_mixins:
            if hasattr(self, mixin):
                await getattr(self, mixin)(msg)

    def on_close(self) -> None:  # noqa: ANN101
        """Handle opening the connection and calls any on_close mixins.

        The closing mixin functions are called as new asyncio Tasks. However, this means that it is not guaranteed
        that the mixin functions are called before the connection is closed.
        """
        for mixin in close_mixins:
            if hasattr(self, mixin):
                asyncio.create_task(getattr(self, mixin)())

    async def send_message(self, msg: dict) -> None:  # noqa: ANN101
        """Send a message to the client.

        :param msg: The message to send.
        :type msg: dict
        """
        await self.write_message(json.dumps(msg))
