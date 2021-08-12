import asyncio
import bleach
import json
import logging


logger = logging.getLogger(__name__)


def safe_text(text: str) -> str:
    return bleach.clean(text,
                        tags=['strong', 'em'],
                        attributes=[],
                        styles=[],
                        protocols=[],
                        strip=True,
                        strip_comments=True)


class MessagesMixin():

    broadcast_messages_mqtt_task = None

    async def setup_messages_task(self):
        self.broadcast_messages_mqtt_task = asyncio.create_task(self.on_mqtt_messages(f'messages/broadcast'))

    async def send_broadcast_message(self, message):
        await self.mqtt.publish(f'messages/broadcast',
                                payload=json.dumps({
                                    'message': safe_text(message['payload']['message'])
                                }))

    async def receive_broadcast_message(self, message):
        await self.send_message({
            'type': 'broadcast-message',
            'payload': {
                'message': message['message'],
            }
        })

    async def send_user_message(self, message):
        await self.mqtt.publish(f'user/{message["payload"]["user"]["id"]}/message',
                                payload=json.dumps({
                                    'user': {
                                        'id': self.user.id,
                                        'name': self.user.name,
                                        'avatar': f'{self.config["server"]["prefixes"]["avatars"]}/{self.user.avatar}'
                                    },
                                    'message': safe_text(message['payload']['message'])
                                }))

    async def receive_user_message(self, message):
        if not self.user.blocked_users or message['user']['id'] not in self.user.blocked_users:
            await self.send_message({
                'type': 'user-message',
                'payload': {
                    'user': message['user'],
                    'message': message['message']
                }
            })

    async def send_request_video_chat_message(self, message):
        await self.mqtt.publish(f'user/{message["payload"]["user"]["id"]}/request-video-chat',
                                payload=json.dumps({
                                    'user': {
                                        'id': self.user.id,
                                        'name': self.user.name,
                                        'avatar': f'{self.config["server"]["prefixes"]["avatars"]}/{self.user.avatar}'
                                    }
                                }))

    async def receive_request_video_chat_message(self, message):
        if not self.user.blocked_users or message['user']['id'] not in self.user.blocked_users:
            await self.send_message({
                'type': 'request-video-chat',
                'payload': {
                    'user': message['user']
                }
            })

    async def send_accept_video_chat_message(self, message):
        await self.mqtt.publish(f'jitsi-rooms/_private/enter',
                                payload=json.dumps({
                                    'users': [self.user.id, message['payload']['user']['id']]
                                }))

    def teardown_messages_task(self):
        if self.broadcast_messages_mqtt_task:
            self.broadcast_messages_mqtt_task.cancel()
