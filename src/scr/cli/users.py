import asyncio
import click


async def add_user():
    print('Yes')


@click.command()
def add():
    """Add a user"""
    asyncio.get_event_loop().run_until_complete(add_user())


@click.command()
def remove():
    """Remove a user"""
    pass


@click.group()
def users():
    """SCR User management"""
    pass


users.add_command(add)
users.add_command(remove)
