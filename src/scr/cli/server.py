import asyncpg
import click
import importlib
import logging
import os
import tornado

from tornado.web import RedirectHandler

from ..db import setup_db
from ..handlers.web import ClientAPIHandler

logger = logging.getLogger('scr.server')


async def make_app():
    settings = {
        'debug': True,
        'static_path': os.path.join(os.path.dirname(importlib.machinery.PathFinder().
                                                    find_module('scr').get_filename()),
                                    'static'),
        'static_handler_args': {'default_filename': 'index.html'},
        'include_version': False,
        'pool': await asyncpg.create_pool(dsn='postgresql://dev:devPWD@localhost/senior-common-room'),
    }

    app = tornado.web.Application([
        (r'/', RedirectHandler, {'url': '/static/', 'permanent': False}),
        ('/websocket', ClientAPIHandler),
    ], **settings)
    app.listen(6543)


@click.group()
def server():
    """Server management"""
    pass


@click.command()
def run():
    """Run the SCR Server"""
    logger.info('Server starting')
    tornado.ioloop.IOLoop.current().add_callback(setup_db)
    tornado.ioloop.IOLoop.current().add_callback(make_app)
    logger.debug('Server running')
    tornado.ioloop.IOLoop.current().start()


server.add_command(run)
