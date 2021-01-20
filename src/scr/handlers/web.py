import asyncio
import asyncio_mqtt
import asyncpg
import json

from hashlib import sha3_256
from secrets import token_hex

from tornado.websocket import WebSocketHandler


class ClientAPIHandler(WebSocketHandler):
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
            await self.authenticate(data)
        elif data['type'] == 'enterRoom':
            self.tasks['rooms'][data['room']] = asyncio.create_task(self.enter_room(data['room']))
        elif data['type'] == 'leaveRoom':
            await self.leave_room(data['room'])
        # else:
        #     print(message)

    def on_close(self):
        for task in self.tasks['rooms'].values():
            task.cancel()
        asyncio.create_task(self.mqtt.disconnect())

    def send_message(self, data):
        self.write_message(json.dumps(data))

    async def enter_room(self, room_name):
        """Enter the given room."""
        async with self.mqtt.filtered_messages(f'rooms/{room_name}') as messages:
            await self.mqtt.subscribe(f'rooms/{room_name}')
            async for msg in messages:
                self.send_message({'type': 'test', 'data': msg.payload.decode()})

    async def leave_room(self, room_name):
        if room_name in self.tasks['rooms']:
            await self.mqtt.unsubscribe(f'rooms/{room_name}')
            self.tasks['rooms'][room_name].cancel()
            del self.tasks['rooms'][room_name]

    async def authenticate(self, data):
        """Authenticate the user.

        Requires parameters "email" and either "password" or "accessToken". Access tokens are only valid for 24 hours.
        Regular calls to authenticate generate a new access token.
        """
        if 'email' in data and 'password' in data:
            async with self.application.settings['pool'].acquire() as conn:
                result = await conn.fetchrow('SELECT * FROM scr_users WHERE email = $1', data['email'])
                if result:
                    hash = sha3_256()
                    hash.update(result.get('salt').encode())
                    hash.update(b'$$')
                    hash.update(data['password'].encode())
                    if hash.hexdigest() == result.get('password'):
                        created = False
                        while not created:
                            try:
                                self.access_token = token_hex(64)
                                await conn.execute('UPDATE scr_users SET access_token = $1, access_token_timestamp = now() WHERE id = $2',  # noqa: E501
                                                   self.access_token,
                                                   result.get('id'))
                                created = True
                            except asyncpg.PostgresError:
                                pass
                        self.send_message({
                            'type': 'authenticated',
                            'email': result.get('email'),
                            'name': result.get('name'),
                            'accessToken': self.access_token,
                        })
                    else:
                        self.send_message({'type': 'authenticationFailed'})
                else:
                    self.send_message({'type': 'authenticationFailed'})
        elif 'email' in data and 'accessToken' in data:
            async with self.application.settings['pool'].acquire() as conn:
                result = await conn.fetchrow("SELECT * FROM scr_users WHERE email = $1 AND access_token = $2 AND access_token_timestamp + interval '24 hour'> now()",  # noqa: E501
                                             data['email'],
                                             data['accessToken'])
                if result:
                    created = False
                    while not created:
                        try:
                            self.access_token = token_hex(64)
                            await conn.execute('UPDATE scr_users SET access_token = $1, access_token_timestamp = now() WHERE id = $2',  # noqa: E501
                                               self.access_token,
                                               result.get('id'))
                            created = True
                        except asyncpg.PostgresError:
                            pass
                    self.send_message({
                        'type': 'authenticated',
                        'email': result.get('email'),
                        'name': result.get('name'),
                        'accessToken': self.access_token,
                    })
                else:
                    self.send_message({'type': 'authenticationFailed'})
        else:
            self.send_message({'type': 'authenticationFailed'})
