import asyncio
import click
import logging

from sqlalchemy.future import select

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


async def async_add_role_to_user(config, email, role):
    async with create_sessionmaker(config['database']['dsn'])() as session:
        async with session.begin():
            query = select(User).filter(User.email == email)
            result = await session.execute(query)
            user = result.scalars().first()
            if user:
                if role not in user.roles:
                    user.roles.append(role)


@click.command()
@click.pass_context
@click.option('--email', required=True, prompt='E-Mail')
@click.option('--role', required=True, prompt='Role')
def add_role_to_user(ctx, email, role):
    asyncio.run(async_add_role_to_user(ctx.obj['config'], email, role))


async def async_remove_role_from_user(config, email, role):
    async with create_sessionmaker(config['database']['dsn'])() as session:
        async with session.begin():
            query = select(User).filter(User.email == email)
            result = await session.execute(query)
            user = result.scalars().first()
            if user:
                if role in user.roles:
                    user.roles.remove(role)


@click.command()
@click.pass_context
@click.option('--email', required=True, prompt='E-Mail')
@click.option('--role', required=True, prompt='Role')
def remove_role_from_user(ctx, email, role):
    asyncio.run(async_remove_role_from_user(ctx.obj['config'], email, role))


database.add_command(create)
database.add_command(add_user)
database.add_command(add_role_to_user)
database.add_command(remove_role_from_user)
