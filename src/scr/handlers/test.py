from hashlib import sha3_256
from secrets import token_hex
from tornado.web import RequestHandler

from ..db import create_update_db


class TestHandler(RequestHandler):

    async def post(self):
        await self._reset_db()
        for obj in self.get_arguments('obj'):
            await getattr(self, f'_create_{obj}')()

    async def _reset_db(self):
        async with self.application.settings['pool'].acquire() as conn:
            await conn.execute('DROP TABLE IF EXISTS scr_versions')
            await conn.execute('DROP TABLE IF EXISTS scr_users_rooms')
            await conn.execute('DROP TABLE IF EXISTS scr_rooms')
            await conn.execute('DROP TABLE IF EXISTS scr_users')
        await create_update_db(self.settings['config'])

    async def _create_user1(self):
        async with self.application.settings['pool'].acquire() as conn:
            salt = token_hex(32)
            hash = sha3_256()
            hash.update(salt.encode())
            hash.update(b'$$test')
            password = hash.hexdigest()
            await conn.execute('INSERT INTO scr_users(email, salt, password, name, created_at) VALUES($1, $2, $3, $4, now())',  # NOQA: E501
                               'test1@example.com',
                               salt,
                               password,
                               'Dr Test Admin')
