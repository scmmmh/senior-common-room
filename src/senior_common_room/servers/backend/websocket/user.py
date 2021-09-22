"""WebsocketHandler mixin for user-related functionality."""
import logging

from sqlalchemy import select, and_

from senior_common_room.models import User

logger = logging.getLogger(__name__)


class UserMixin():
    """User-focused WebsocketHandler mixin."""

    async def user_on_open(self) -> None:  # noqa: ANN101
        """Handle opening a websocket connection."""
        await self.send_message({'type': 'authentication-required'})

    async def user_on_message(self, msg: dict) -> None:  # noqa: ANN101
        """Handle user-related websocket messages.

        :param msg: The message to handle
        :type msg: dict
        """
        if msg['type'] == 'authenticate':
            await self.user_authenticate(msg)

    async def user_authenticate(self, msg: dict) -> None:  # noqa: ANN101
        """Attempt to authenticate the given payload.

        :param msg: The authentication message
        :type msg: dict
        """
        async with self.Session() as session:
            logger.debug(f'Authenticating {msg["payload"]["email"]}')
            query = select(User).filter(and_(User.email == msg['payload']['email'],
                                             User.token == msg['payload']['token'],
                                             User.status == 'active'))
            result = await session.execute(query)
            user = result.scalars().first()
            if user:
                self.user = user
                await self.send_message({'type': 'authenticated'})
            else:
                await self.send_message({'type': 'authentication-failed'})
