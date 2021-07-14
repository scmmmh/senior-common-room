import json
import jwt
import logging


logger = logging.getLogger(__name__)


class JitsiMixin():

    jitsi_room_name = None

    async def request_jitsi_room(self, message):
        self.jitsi_room_name = message['payload']['name']
        await self.mqtt.publish(f'jitsi-rooms/{self.jitsi_room_name}/enter',
                                payload=json.dumps({
                                    'user': self.user.id,
                                    'subject': message['payload']['subject']
                                }).encode())

    async def enter_jitsi_room(self, message):
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
        logger.debug(f'Entered Jitsi Room {self.jitsi_room_name}')

    async def leave_jitsi_room(self, message):
        logger.debug(f'Leaving Jitsi Room {self.jitsi_room_name}')
        await self.mqtt.publish(f'jitsi-rooms/{self.jitsi_room_name}/leave',
                                payload=json.dumps({
                                    'user': self.user.id,
                                }).encode())
        self.jitsi_room_name = None

    async def jitsi_shutdown(self):
        if self.jitsi_room_name:
            await self.mqtt.publish(f'jitsi-rooms/{self.jitsi_room_name}/leave',
                                    payload=json.dumps({
                                        'user': self.user.id,
                                    }).encode())
