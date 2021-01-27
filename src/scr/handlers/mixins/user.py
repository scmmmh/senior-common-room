from asyncpg import PostgresError
from hashlib import sha3_256
from secrets import token_hex


class UserMixin():

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
                        self.user_id = result.get('id')
                        self.user_name = result.get('name')
                        created = False
                        while not created:
                            try:
                                self.access_token = token_hex(64)
                                await conn.execute('UPDATE scr_users SET access_token = $1, access_token_timestamp = now() WHERE id = $2',  # noqa: E501
                                                   self.access_token,
                                                   result.get('id'))
                                created = True
                            except PostgresError:
                                pass
                        await conn.execute('DELETE FROM scr_users_rooms WHERE user_id = $1', result.get('id'))
                        self.send_message({
                            'type': 'authenticated',
                            'data': {
                                'id': str(result.get('id')),
                                'email': result.get('email'),
                                'name': result.get('name'),
                                'accessToken': self.access_token,
                            },
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
                    self.user_id = result.get('id')
                    self.user_name = result.get('name')
                    created = False
                    while not created:
                        try:
                            self.access_token = token_hex(64)
                            await conn.execute('UPDATE scr_users SET access_token = $1, access_token_timestamp = now() WHERE id = $2',  # noqa: E501
                                               self.access_token,
                                               result.get('id'))
                            created = True
                        except PostgresError:
                            pass
                    await conn.execute('DELETE FROM scr_users_rooms WHERE user_id = $1', result.get('id'))
                    self.send_message({
                        'type': 'authenticated',
                        'data': {
                            'id': str(result.get('id')),
                            'email': result.get('email'),
                            'name': result.get('name'),
                            'accessToken': self.access_token,
                        },
                    })
                else:
                    self.send_message({'type': 'authenticationFailed'})
        else:
            self.send_message({'type': 'authenticationFailed'})
