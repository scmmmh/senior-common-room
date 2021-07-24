import asyncio
import json
import logging


logger = logging.getLogger(__name__)


class MessagesMixin():

    messages_mqtt_task = None

    async def setup_messages_task(self):
        self.messages_mqtt_task = asyncio.create_task(self.on_mqtt_messages(f'messages/broadcast'))

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


    def teardown_messages_task(self):
        if self.messages_mqtt_task:
            self.messages_mqtt_task.cancel()
