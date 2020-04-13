from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from secrets import token_hex
from sqlalchemy import and_

from ..session import require_logged_in
from ..models import Room, RoomRole


@view_config(route_name='room.create', renderer='scr:templates/room/create.jinja2')
@require_logged_in()
def create(request):
    if request.method == 'POST':
        pass
    return {}


@view_config(route_name='room.view', renderer='scr:templates/room/view.jinja2')
@require_logged_in()
def view(request):
    result = request.dbsession.query(Room, RoomRole).\
        join(RoomRole).filter(and_(Room.id == request.matchdict['rid'],
                                   RoomRole.user_id == request.current_user.id)).\
        first()
    if result:
        room, role = result
        if role.role == 'host':
            room.jitsi_room = token_hex(32)
            room.jitsi_password = token_hex(8)
            request.dbsession.add(room)
            request.dbsession.flush()
        return {'room': room,
                'role': role}
    else:
        raise HTTPNotFound()
