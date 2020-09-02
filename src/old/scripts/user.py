import click
import transaction

from hashlib import sha512
from secrets import token_hex

from ..models import get_engine, get_session_factory, get_tm_session, User


@click.command()
@click.argument('email')
@click.argument('name')
@click.pass_context
def create_user(ctx, email, name):
    """Create a new user."""
    engine = get_engine(ctx.obj['settings'])
    session_factory = get_session_factory(engine)
    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
        password = click.prompt('Pasword', hide_input=True)
        salt = token_hex(32)
        hash = sha512()
        hash.update(salt.encode('utf-8'))
        hash.update(b'$$')
        hash.update(password.encode('utf-8'))
        user = User(email=email,
                    salt=salt,
                    password=hash.hexdigest(),
                    status='active',
                    groups=[],
                    permissions=[],
                    attributes={'name': name})
        dbsession.add(user)
