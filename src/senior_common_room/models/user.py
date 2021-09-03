from sqlalchemy import (Column, Integer, String)
from sqlalchemy_json import NestedMutableJson

from .meta import Base


class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(length=255), unique=True)
    name = Column(String(length=255))
    token = Column(String(length=255))
    avatar = Column(String(length=255), unique=True)
    timezone = Column(String(length=255))
    roles = Column(NestedMutableJson)
    blocked_users = Column(NestedMutableJson)
    status = Column(String(length=255))
