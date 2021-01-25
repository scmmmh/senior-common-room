import json


class RoomMixin():

    async def get_public_rooms(self):
        async with self.application.settings['pool'].acquire() as conn:
            result = await conn.fetch("SELECT * FROM scr_rooms WHERE type = 'permanent' or type = 'public'")
            if result is not None:
                self.send_message({
                    'type': 'publicRoomsList',
                    'rooms': list(map(lambda r: {'id': r.get('external_id'),
                                                 'label': r.get('label'),
                                                 'lobby': r.get('type') == 'permanent'},
                                      result))
                })

    async def enter_room(self, room_name):
        """Enter the given room."""
        async with self.mqtt.filtered_messages(f'rooms/{room_name}') as messages:
            await self.mqtt.subscribe(f'rooms/{room_name}')
            async with self.application.settings['pool'].acquire() as conn:
                room = await conn.fetchrow('SELECT * FROM scr_rooms WHERE external_id = $1', room_name)
                result = await conn.fetch('SELECT scr_users.* FROM scr_users JOIN scr_users_rooms ON scr_users.id = scr_users_rooms.user_id WHERE scr_users_rooms.room_id = $1',  # noqa: E501
                                          room.get('id'))
                self.send_message({
                    'type': 'roomUsersList',
                    'users': list(map(lambda u: {'id': str(u.get('id')),
                                                 'name': u.get('name')},
                                      result))
                })
                await conn.execute('INSERT INTO scr_users_rooms(user_id, room_id) VALUES($1, $2)',
                                   self.user_id,
                                   room.get('id'))
            await self.mqtt.publish(f'rooms/{room_name}', json.dumps({'type': 'userEntersRoom',
                                                                      'data': {'id': str(self.user_id),
                                                                               'name': self.user_name}}))
            async for msg in messages:
                self.send_message(json.loads(msg.payload.decode()))

    async def leave_room(self, room_name):
        if room_name in self.tasks['rooms']:
            await self.mqtt.unsubscribe(f'rooms/{room_name}')
            self.tasks['rooms'][room_name].cancel()
            del self.tasks['rooms'][room_name]
            async with self.application.settings['pool'].acquire() as conn:
                room = await conn.fetchrow('SELECT * FROM scr_rooms WHERE external_id = $1', room_name)
                await conn.execute('DELETE FROM scr_users_rooms WHERE room_id = $2 AND user_id = $1',
                                   self.user_id,
                                   room.get('id'))
            await self.mqtt.publish(f'rooms/{room_name}', json.dumps({'type': 'userLeavesRoom',
                                                                      'data': {'id': str(self.user_id)}}))
