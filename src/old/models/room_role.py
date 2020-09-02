from sqlalchemy import (Column, Index, Integer, Unicode, ForeignKey, DateTime)
from sqlalchemy.orm import relationship

from .meta import Base


class RoomRole(Base):

    __tablename__ = 'room_roles'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    room_id = Column(Integer, ForeignKey('rooms.id'))
    role = Column(Unicode(255))
    ping = Column(DateTime())

    room = relationship('Room')
    user = relationship('User')


Index('room_roles_ids_ix', RoomRole.user_id, RoomRole.room_id)
