import asyncio
import json
import logging


logger = logging.getLogger(__name__)


class MessagesMixin():

    broadcast_messages_mqtt_task = None

    async def setup_messages_task(self):
        self.broadcast_messages_mqtt_task = asyncio.create_task(self.on_mqtt_messages(f'messages/broadcast'))

    async def send_broadcast_message(self, message):
        await self.mqtt.publish(f'messages/broadcast',
                                payload=json.dumps({
                                    'message': message['payload']['message']
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
                                    'message': message['payload']['message']
                                }))

    async def receive_user_message(self, message):
        await self.send_message({
            'type': 'user-message',
            'payload': {
                'user': message['user'],
                'message': message['message']
            }
        })

    def teardown_messages_task(self):
        if self.broadcast_messages_mqtt_task:
            self.broadcast_messages_mqtt_task.cancel()
