import click
import asyncpg
import importlib
import logging
import tornado.ioloop
import os

from tornado.web import RedirectHandler

from .db import setup_db
from .handlers.web import ClientAPIHandler


logger = logging.getLogger('scr')


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
@click.option('-v', '--verbose', count=True)
def cli(verbose=0):
    """Senior Common Room CLI"""
    if verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif verbose > 1:
        logging.basicConfig(level=logging.DEBUG)


@click.command()
def run_server():
    """Run the SCR Server"""
    logger.info('Server starting')
    tornado.ioloop.IOLoop.current().add_callback(setup_db)
    tornado.ioloop.IOLoop.current().add_callback(make_app)
    logger.debug('Server running')
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    cli.add_command(run_server)

    cli()
