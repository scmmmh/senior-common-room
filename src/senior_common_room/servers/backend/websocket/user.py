"""WebsocketHandler mixin for user-related functionality."""


class UserMixin():
    """User-focused WebsocketHandler mixin."""

    async def user_on_open(self) -> None:  # noqa: ANN101
        """Handle opening a websocket connection."""
        await self.send_message({'type': 'authentication-required'})
