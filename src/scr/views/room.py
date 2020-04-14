import jwt
import re

from datetime import datetime, timedelta
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.view import view_config
from secrets import token_hex
from sqlalchemy import and_

from ..session import require_logged_in
from ..models import Room, RoomRole, User
from ..util import Validator, get_config_setting


def slugify(text):
    slug = []
    for character in text:
        if re.match('[a-zA-Z0-9]', character):
            slug.append(character)
        else:
            slug.append('-')
    slug = ''.join(slug)
    while '--' in slug:
        slug.replace('--', '-')
    return slug.lower()


create_room_schema = {'name': {'type': 'string', 'empty': False},
                      'csrf_token': {'type': 'string'}}


@view_config(route_name='room.create', renderer='scr:templates/room/create.jinja2')
@require_logged_in()
def create(request):
    if request.method == 'POST':
        validator = Validator(create_room_schema)
        if validator.validate(request.params):
            slug = slugify(request.params['name'])
            room = request.dbsession.query(Room).filter(Room.slug == slug).first()
            if room:
                return {'errors': {'name': ['A room with this name already exists']},
                        'values': request.params}
            room = Room(name=request.params['name'],
                        slug=slug)
            room_role = RoomRole(user=request.current_user,
                                 room=room,
                                 role='host')
            request.dbsession.add(room)
            request.dbsession.add(room_role)
            request.dbsession.flush()
            return HTTPFound(request.route_url('room.edit', rid=room.id))
        else:
            return {'errors': validator.errors, 'values': request.params}
    return {}


@view_config(route_name='room.view', renderer='scr:templates/room/view.jinja2')
@require_logged_in()
def view(request):
    if re.match('[0-9]+', request.matchdict['rid']):
        result = request.dbsession.query(Room, RoomRole).\
            join(RoomRole).filter(and_(Room.id == request.matchdict['rid'],
                                       RoomRole.user_id == request.current_user.id)).\
            first()
    else:
        result = request.dbsession.query(Room, RoomRole).\
            join(RoomRole).filter(and_(Room.slug == request.matchdict['rid'],
                                       RoomRole.user_id == request.current_user.id)).\
            first()
    if result:
        room, role = result
        token = None
        if role.role == 'host':
            if room.jitsi_room is None:
                room.jitsi_room = token_hex(32)
                room.jitsi_password = token_hex(8)
                request.dbsession.add(room)
                request.dbsession.flush()
            payload = {'iss': get_config_setting(request, 'jitsi.meet.app_id'),
                       'aud': get_config_setting(request, 'jitsi.meet.app_id'),
                       'room': room.jitsi_room,
                       'exp': (datetime.now() + timedelta(minutes=5)).timestamp(),
                       'sub': get_config_setting(request, 'jitsi.meet.url')}
            token = jwt.encode(payload,
                               get_config_setting(request, 'jitsi.meet.secret'),
                               algorithm='HS256').decode('utf-8')
        return {'room': room,
                'role': role,
                'jwt': token}
    else:
        raise HTTPNotFound()


edit_room_schema = {'name': {'type': 'string', 'empty': False},
                    'host': {'type': 'string'},
                    'participant': {'type': 'string'},
                    'csrf_token': {'type': 'string'}}


@view_config(route_name='room.edit', renderer='scr:templates/room/edit.jinja2')
@require_logged_in()
def edit(request):
    room = request.dbsession.query(Room).\
        join(RoomRole).filter(and_(Room.id == request.matchdict['rid'],
                                   RoomRole.user_id == request.current_user.id,
                                   RoomRole.role == 'host')).\
        first()
    if room:
        users = []
        for user in request.dbsession.query(User):
            host = False
            participant = False
            for role in room.users:
                if role.user_id == user.id:
                    if role.role == 'host':
                        host = True
                    else:
                        participant = True
            users.append({'user': user, 'host': host, 'participant': participant})
        if request.method == 'POST':
            validator = Validator(edit_room_schema)
            if validator.validate(request.params):
                slug = slugify(request.params['name'])
                existing = request.dbsession.query(Room).filter(and_(Room.slug == slug,
                                                                     Room.id != request.matchdict['rid'])).first()
                if existing:
                    return {'room': room, 'users': users, 'errors': validator.errors, 'values': request.params}
                room.name = request.params['name']
                room.slug = slug
                hosts = request.params.getall('host')
                participants = [pid for pid in request.params.getall('participant') if pid not in hosts]
                for role in room.users:
                    if role.role == 'host':
                        if str(role.user_id) not in hosts and role.user_id != request.current_user.id:
                            if str(role.user_id) in participants:
                                role.role = 'participant'
                                participants.remove(str(role.user_id))
                            else:
                                request.dbsession.delete(role)
                        elif str(role.user_id) in hosts:
                            hosts.remove(str(role.user_id))
                    else:
                        if str(role.user_id) not in participants:
                            if str(role.user_id) in hosts:
                                role.role = 'host'
                                hosts.remove(str(role.user_id))
                            else:
                                request.dbsession.delete(role)
                        elif str(role.user_id) in participants:
                            participants.remove(str(role.user_id))
                for uid in hosts:
                    user = request.dbsession.query(User).filter(User.id == uid).first()
                    if user:
                        request.dbsession.add(RoomRole(room=room, user=user, role='host'))
                for uid in participants:
                    user = request.dbsession.query(User).filter(User.id == uid).first()
                    if user:
                        request.dbsession.add(RoomRole(room=room, user=user, role='participant'))
                request.dbsession.add(room)
                return HTTPFound(request.route_url('root'))
            else:
                return {'room': room,
                        'users': users,
                        'errors': {'name': ['A room with this name already exists']},
                        'values': request.params}
        return {'room': room,
                'users': users}
    else:
        raise HTTPNotFound()


@view_config(route_name='room.close')
@require_logged_in()
def close(request):
    room = request.dbsession.query(Room).\
        join(RoomRole).filter(and_(Room.id == request.matchdict['rid'],
                                   RoomRole.user_id == request.current_user.id,
                                   RoomRole.role == 'host')).\
        first()
    if room:
        room.jitsi_room = None
        room.jitsi_password = None
        request.dbsession.add(room)
        return HTTPFound(request.route_url('root'))
    else:
        return HTTPFound(request.route_url('root'))
