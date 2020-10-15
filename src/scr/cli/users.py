import asyncio
import asyncpg
import click
import logging

from hashlib import sha3_256
from secrets import token_hex


logger = logging.getLogger('scr.users')


async def add_user(config, email, name, password):
    """Add a new user to the database."""
    async with asyncpg.create_pool(dsn=config.get('database', 'dsn')) as pool:
        async with pool.acquire() as conn:
            try:
                async with conn.transaction():
                    salt = token_hex(32)
                    hash = sha3_256()
                    hash.update(salt.encode())
                    hash.update(b'$$')
                    hash.update(password.encode())
                    password = hash.hexdigest()
                    await conn.execute('''INSERT INTO scr_users(email, salt, password, name, created_at)
VALUES($1, $2, $3, $4, now())''',
                                       email,
                                       salt,
                                       password,
                                       name)
                logger.debug('User created')
            except asyncpg.exceptions.UniqueViolationError:
                logger.error(f'A user with the e-mail address {email} already exists')


@click.command()
@click.option('--email', prompt='E-Mail', help='E-Mail address of the new user')
@click.option('--name', prompt='Name', help='Name of the new user')
@click.option('--password', prompt='Password', hide_input=True, confirmation_prompt=True,
              help='Password of the new user')
@click.pass_context
def add(ctx, email, name, password):
    """Add a user"""
    asyncio.get_event_loop().run_until_complete(add_user(ctx.obj['config'],
                                                         email,
                                                         name,
                                                         password))


async def remove_user(config, email):
    """Remove a user from the database."""
    async with asyncpg.create_pool(dsn=config.get('database', 'dsn')) as pool:
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute('DELETE FROM scr_users WHERE email = $1', email)
            logger.debug('User removed')


@click.command()
@click.option('--email', prompt='E-Mail', help='E-Mail address of the user to remove')
@click.pass_context
def remove(ctx, email):
    """Remove a user"""
    asyncio.get_event_loop().run_until_complete(remove_user(ctx.obj['config'], email))


@click.group()
def users():
    """SCR User management"""
    pass


users.add_command(add)
users.add_command(remove)
