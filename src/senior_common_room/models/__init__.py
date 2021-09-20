"""Database models and connections."""
import logging

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker

from .meta import Base  # noqa
from .user import User  # noqa


logger = logging.getLogger(__name__)


def create_engine(dsn: str) -> AsyncEngine:
    """Create a database engine.

    :param dsn: The data source name of the database to connect to.
    :type dsn: str
    :return: The database engine.
    :rtype: AsyncEngine
    """
    logger.debug(f'Creating engine for {dsn}')
    return create_async_engine(dsn)


def create_sessionmaker(dsn: str) -> AsyncSession:
    """Create a database session.

    :param dsn: The data source name of the database to connect to.
    :type dsn: str
    :return: The database engine.
    :rtype: AsyncSession
    """
    logger.debug('Creating sessionmaker')
    return sessionmaker(
        create_engine(dsn),
        expire_on_commit=False,
        class_=AsyncSession
    )
