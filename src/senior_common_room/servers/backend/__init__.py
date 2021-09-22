"""The backend server."""
from tornado.web import Application

from .websocket import WebsocketHandler


def create_application(config: dict) -> Application:
    """Create a new tornado Application for the backend server.

    :param config: The configuration settings
    :type config: dict
    :return: The new application
    :rtype: Application
    """
    app = Application(
        [
            (r'/api/websocket', WebsocketHandler, {'config': config}),
        ],
        websocket_max_message_size=14680064)
    return app
