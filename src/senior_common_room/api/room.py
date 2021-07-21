import asyncio
import json
import logging


logger = logging.getLogger(__name__)


class RoomMixin():

    room_name = None

    async def enter_room(self, message):
        self.room_name = message['payload']['room']
        self.room_mqtt_task = asyncio.create_task(self.on_mqtt_messages(f'room/{self.room_name}/+'))

    async def room_set_avatar_location(self, message):
        await self.mqtt.publish(f'room/{self.room_name}/set-avatar-location',
                                payload=json.dumps({
                                    'user': {
                                        'id': self.user.id,
                                        'avatar': f'{self.config["server"]["prefixes"]["avatars"]}/{self.user.avatar}',
                                        'name': self.user.name,
                                        'roles': self.user.roles,
                                    },
                                    'room': message['payload']['room'],
                                    'x': message['payload']['x'],
                                    'y': message['payload']['y']
                                }))

    async def room_update_avatar_location(self, message):
        if message['user']['id'] != self.user.id and message['room'] == self.room_name:
            await self.send_message({
                'type': 'update-avatar-location',
                'payload': {
                    'user': message['user'],
                    'room': message['room'],
                    'x': message['x'],
                    'y': message['y']
                }
            })

    async def room_remove_avatar(self, message):
        if message['user'] != self.user.id and message['room'] == self.room_name:
            await self.send_message({
                'type': 'remove-avatar',
                'payload': {
                    'user': message['user']
                }
            })

    async def leave_room(self, message):
        await self.mqtt.publish(f'room/{self.room_name}/leave',
                                payload=json.dumps({
                                    'user': self.user.id,
                                    'room': self.room_name,
                                }))
        await self.mqtt.unsubscribe(f'room/{self.room_name}/+')
        if self.room_mqtt_task:
            self.room_mqtt_task.cancel()
            self.room_mqtt_task = None
        self.room_name = None
