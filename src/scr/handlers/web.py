import asyncio
import asyncio_mqtt
import json

from tornado.websocket import WebSocketHandler

from .mixins import UserMixin, RoomMixin


class ClientAPIHandler(WebSocketHandler, UserMixin, RoomMixin):
    user_id = None
    user_name = ''

    async def open(self):
        self.access_token = None
        self.send_message({'type': 'authenticate'})
        self.mqtt = asyncio_mqtt.Client(self.application.settings['config'].get('mqtt', 'host'),
                                        port=self.application.settings['config'].getint('mqtt', 'port'))
        self.tasks = {'rooms': {}}
        await self.mqtt.connect()

    async def on_message(self, message):
        data = json.loads(message)
        if data['type'] == 'authenticate':
            await self.authenticate(data['data'])
        elif data['type'] == 'getPublicRooms':
            await self.get_public_rooms()
        elif data['type'] == 'enterRoom':
            self.tasks['rooms'][data['data']['room']] = \
                asyncio.create_task(self.enter_room(data['data']['room']))
        elif data['type'] == 'leaveRoom':
            await self.leave_room(data['data']['room'])
        # else:
        #     print(message)

    def on_close(self):
        for task in self.tasks['rooms'].values():
            task.cancel()
        asyncio.create_task(self.mqtt.disconnect())

    def send_message(self, data):
        self.write_message(json.dumps(data))
