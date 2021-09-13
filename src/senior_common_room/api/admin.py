import asyncio
import json
import logging


logger = logging.getLogger(__name__)


class AdminMixin():

    admin_messages_mqtt_task = None

    async def setup_admin_messages_task(self):
        self.admin_messages_mqtt_task = asyncio.create_task(self.on_mqtt_messages(f'messages/admin'))

    async def send_ui_reload(self):
        if 'admin' in self.user.roles:
            await self.mqtt.publish(f'messages/admin', payload=json.dumps({
                                        'action': 'ui-reload'
                                    }))

    async def receive_ui_reload(self):
        await self.send_message({
            'type': 'ui-reload'
        })

    def teardown_admin_task(self):
        if self.admin_messages_mqtt_task:
            self.admin_messages_mqtt_task.cancel()
