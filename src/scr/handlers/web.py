import asyncpg
import json

from hashlib import sha3_256
from secrets import token_hex

from tornado.websocket import WebSocketHandler


class ClientAPIHandler(WebSocketHandler):
    def open(self):
        print("WebSocket opened")
        self.access_token = None
        self.send_message({'type': 'notAuthenticated'})

    async def on_message(self, message):
        data = json.loads(message)
        if data['type'] == 'authenticate':
            await self.authenticate(data)
        else:
            print(message)

    def on_close(self):
        print("WebSocket closed")
        pass

    def send_message(self, data):
        self.write_message(json.dumps(data))

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
                                await conn.execute('UPDATE scr_users SET access_token = $1, access_token_timestamp = now() WHERE id = $2',
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
                        self.send_message({'type': 'notAuthenticated'})
                else:
                    self.send_message({'type': 'notAuthenticated'})
        elif 'email' in data and 'accessToken' in data:
            async with self.application.settings['pool'].acquire() as conn:
                result = await conn.fetchrow("SELECT * FROM scr_users WHERE email = $1 AND access_token = $2 AND access_token_timestamp + interval '24 hour'> now()",
                                             data['email'],
                                             data['accessToken'])
                if result:
                    created = False
                    while not created:
                        try:
                            self.access_token = token_hex(64)
                            await conn.execute('UPDATE scr_users SET access_token = $1, access_token_timestamp = now() WHERE id = $2',
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
                    self.send_message({'type': 'notAuthenticated'})
        else:
            self.send_message({'type': 'notAuthenticated'})
