from datetime import datetime
from sqlalchemy import (Column, Index, Integer, Unicode, DateTime)
from sqlalchemy.orm import relationship

from .meta import Base


class Room(Base):

    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(191))
    slug = Column(Unicode(191))
    jitsi_password = Column(Unicode(255))
    jitsi_room = Column(Unicode(255))
    guest_password = Column(Unicode(255))
    created = Column(DateTime, default=datetime.now)

    users = relationship('RoomRole', cascade="all, delete-orphan")

    def allow(self, user, action):
        """Check whether the given user is allowed to undertake the given action.

        :param user: The user to check for
        :type user: :class:`~toja.models.user.User`
        :param action: The action to check (view, edit, delete)
        :type action: ``str``
        """
        if action == 'view':
            return True
        elif action == 'edit':
            return user is not None and user.id == self.id
        elif action == 'delete':
            return user is not None and user.id == self.id
        else:
            return False


Index('rooms_slug_ix', Room.slug, unique=True, mysql_length=191)
