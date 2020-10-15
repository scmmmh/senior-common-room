import click
import logging
import os
import sys

from configparser import ConfigParser

from .users import users
from .server import server


logger = logging.getLogger('scr')
DEFAULT_CONFIG = {
    'server': {
        'host': '127.0.0.1',
        'port': 6543,
        'debug': False,
    },
    'mqtt': {
        'host': '127.0.0.1',
        'port': 1883,
    }
}


@click.group()
@click.option('-v', '--verbose', count=True)
@click.option('-c', '--config', default='production.ini')
@click.pass_context
def cli(ctx, verbose, config):
    """Senior Common Room CLI"""
    ctx.ensure_object(dict)
    if verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif verbose > 1:
        logging.basicConfig(level=logging.DEBUG)
    logger.debug('Logging set up')
    if not os.path.exists(config):
        logger.error(f'Configuration file {config} not found')
        sys.exit(1)
    parser = ConfigParser()
    parser.read_dict(DEFAULT_CONFIG)
    parser.read(config)
    ctx.obj['config'] = parser


cli.add_command(server)
cli.add_command(users)
