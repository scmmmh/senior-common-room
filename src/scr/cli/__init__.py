import click
import logging

from .users import user
from .server import server


logger = logging.getLogger('scr')


@click.group()
@click.option('-v', '--verbose', count=True)
def cli(verbose=0):
    """Senior Common Room CLI"""
    if verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif verbose > 1:
        logging.basicConfig(level=logging.DEBUG)
    logger.debug('Logging set up')


cli.add_command(server)
cli.add_command(user)
