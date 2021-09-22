"""Database models and connections."""
import logging

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from typing import Union

from .meta import Base  # noqa
from .user import User  # noqa


logger = logging.getLogger(__name__)
engines = {}


def create_engine(dsn: str) -> AsyncEngine:
    """Create a database engine.

    Only a single engine is created for each ``dsn``.

    :param dsn: The data source name of the database to connect to.
    :type dsn: str
    :return: The database engine.
    :rtype: AsyncEngine
    """
    if dsn not in engines:
        logger.debug(f'Creating engine for {dsn}')
        engines[dsn] = create_async_engine(dsn)
    return engines[dsn]


def create_sessionmaker(dsn: Union[str, None] = None, engine: Union[AsyncEngine, None] = None) -> AsyncSession:
    """Create a database session.

    Either ``dsn`` or ``engine`` need to be provided. If both are provided, then the ``engine`` parameter has
    precedence.

    :param dsn: The data source name of the database to connect to.
    :type dsn: str
    :param engine: The existing engine to use.
    :type engine: AsyncEngine
    :return: The database engine.
    :rtype: AsyncSession
    """
    logger.debug('Creating sessionmaker')
    if engine is None:
        engine = create_engine(dsn)
    return sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession
    )
