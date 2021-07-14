import logging

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from .meta import Base  # noqa
from .user import User  # noqa


logger = logging.getLogger(__name__)


def create_engine(dsn: str):
    logger.debug(f'Creating engine for {dsn}')
    return create_async_engine(dsn)


def create_sessionmaker(dsn: str):
    logger.debug('Creating sessionmaker')
    return sessionmaker(
        create_engine(dsn),
        expire_on_commit=False,
        class_=AsyncSession
    )
