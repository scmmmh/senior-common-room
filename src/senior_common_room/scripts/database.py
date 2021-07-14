import asyncio
import click
import logging

from ..models import create_engine, create_sessionmaker, Base, User


logger = logging.getLogger(__name__)


@click.group()
def database():
    pass


async def create_database(config):
    async with create_engine(config['database']['dsn']).begin() as conn:
        logger.debug('Dropping existing database tables')
        await conn.run_sync(Base.metadata.drop_all)
        logger.debug('Creating database tables')
        await conn.run_sync(Base.metadata.create_all)
    logger.debug('Database created')


@click.command()
@click.pass_context
def create(ctx):
    asyncio.run(create_database(ctx.obj['config']))


async def create_user(config, email, name):
    async with create_sessionmaker(config['database']['dsn'])() as session:
        async with session.begin():
            session.add(User(email=email, name=name, roles=[]))


@click.command()
@click.pass_context
@click.option('--email', required=True, prompt='E-Mail')
@click.option('--name', required=True, prompt='Name')
def add_user(ctx, email, name):
    asyncio.run(create_user(ctx.obj['config'], email, name))


database.add_command(create)
database.add_command(add_user)
