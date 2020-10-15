import asyncio
import asyncpg
import click
import logging

from hashlib import sha3_256
from secrets import token_hex

from ..db import create_update_db


logger = logging.getLogger('scr.cli.db')


@click.command()
@click.pass_context
def init(ctx):
    """Initialise the database"""
    asyncio.get_event_loop().run_until_complete(create_update_db(ctx.obj['config']))


@click.command()
@click.pass_context
def update(ctx):
    """Update the database"""
    asyncio.get_event_loop().run_until_complete(create_update_db(ctx.obj['config']))


@click.group()
def db():
    """Database management"""
    pass


db.add_command(init)
db.add_command(update)
