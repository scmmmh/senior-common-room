import asyncio
import asyncpg
import click
import importlib
import logging
import os
import tornado

from tornado.web import RedirectHandler

from ..db import verify_db
from ..handlers.web import ClientAPIHandler

logger = logging.getLogger('scr.cli.server')


async def make_app(config):
    pool = await asyncpg.create_pool(dsn=config.get('database', 'dsn'))
    if await verify_db(pool):
        settings = {
            'debug': config.getboolean('server', 'debug'),
            'autorealod': config.getboolean('server', 'autoreload'),
            'static_path': os.path.join(os.path.dirname(importlib.machinery.PathFinder().
                                                        find_module('scr').get_filename()),
                                        'static'),
            'static_handler_args': {'default_filename': 'index.html'},
            'include_version': False,
            'pool': pool,
            'config': config,
        }

        app = tornado.web.Application([
            (r'/', RedirectHandler, {'url': '/static/', 'permanent': False}),
            ('/websocket', ClientAPIHandler),
        ], **settings)
        app.listen(port=config.getint('server', 'port'), address=config.get('server', 'host'))
        logger.debug('Server listening')
    else:
        logger.error('The database is out of date. Please run python -m scr db update')


@click.group()
def server():
    """Server management"""
    pass


@click.command()
@click.pass_context
def run(ctx):
    """Run the SCR Server"""
    logger.info('Server starting')
    loop = asyncio.get_event_loop()
    loop.create_task(make_app(ctx.obj['config']))
    tornado.ioloop.IOLoop.current().start()


server.add_command(run)
