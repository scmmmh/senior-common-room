import asyncio
import json
import jwt
import logging


logger = logging.getLogger(__name__)


class JitsiMixin():

    jitsi_room_name = None
    jitsi_room_mqtt_task = None

    async def request_jitsi_room(self, message):
        self.jitsi_room_name = message['payload']['name']
        await self.mqtt.publish(f'jitsi-rooms/{self.jitsi_room_name}/enter',
                                payload=json.dumps({
                                    'user': self.user.id,
                                    'subject': message['payload']['subject']
                                }).encode())

    async def enter_jitsi_room(self, message):
        self.jitsi_room_name = message['room_name']
        if 'jwt' in self.config['jitsi']:
            encoded_jwt = jwt.encode({
                'iss': self.config['jitsi']['jwt']['application_id'],
                'room': message['url'],
                'sub': '*',
                'aud': self.config['jitsi']['jwt']['client_id']
            }, self.config['jitsi']['jwt']['secret'], algorithm='HS256')
            message['jwt'] = encoded_jwt
        await self.send_message({
            'type': 'open-jitsi-room',
            'payload': message
        })
        self.jitsi_room_mqtt_task = asyncio.create_task(self.on_mqtt_messages(f'jitsi-rooms/{self.jitsi_room_name}/user-list'))
        logger.debug(f'Entered Jitsi Room {self.jitsi_room_name}')

    async def leave_jitsi_room(self):
        if self.jitsi_room_name:
            logger.debug(f'Leaving Jitsi Room {self.jitsi_room_name}')
            await self.mqtt.publish(f'jitsi-rooms/{self.jitsi_room_name}/leave',
                                    payload=json.dumps({
                                        'user': self.user.id,
                                    }).encode())
            self.jitsi_room_name = None
            if self.jitsi_room_mqtt_task:
                self.jitsi_room_mqtt_task.cancel()
            self.jitsi_room_mqtt_task = None
            await self.send_message({
                'type': 'left-jitsi-room'
            })

    async def request_jitsi_room_users(self):
        if self.jitsi_room_name:
            await self.send_mqtt_message(f'jitsi-rooms/{self.jitsi_room_name}/request-user-list')

    async def jitsi_room_user_list(self, message):
        if self.jitsi_room_name:
            await self.send_message({
                'type': 'jitsi-room-users',
                'payload': {
                    'users': message['users']
                }
            })

    async def jitsi_shutdown(self):
        if self.jitsi_room_name:
            await self.mqtt.publish(f'jitsi-rooms/{self.jitsi_room_name}/leave',
                                    payload=json.dumps({
                                        'user': self.user.id,
                                    }).encode())
        if self.jitsi_room_mqtt_task:
            self.jitsi_room_mqtt_task.cancel()
