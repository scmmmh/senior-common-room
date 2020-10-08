import importlib
import tornado.ioloop
import os

from tornado.web import RedirectHandler

from .db import setup_db
from .handlers.web import ClientAPIHandler


def make_app():
    settings = {
        'debug': True,
        'static_path': os.path.join(os.path.dirname(importlib.machinery.PathFinder().
                                                    find_module('scr').get_filename()),
                                    'static'),
        'static_handler_args': {'default_filename': 'index.html'},
        'include_version': False,
    }

    return tornado.web.Application([
        (r'/', RedirectHandler, {'url': '/static/', 'permanent': False}),
        ('/websocket', ClientAPIHandler),
    ], **settings)


if __name__ == "__main__":
    app = make_app()
    app.listen(6543)
    tornado.ioloop.IOLoop.current().add_callback(setup_db)
    tornado.ioloop.IOLoop.current().start()
