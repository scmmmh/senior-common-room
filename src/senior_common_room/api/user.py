import asyncio
import logging
import smtplib
import os

from base64 import b64decode
from email.message import EmailMessage
from email.utils import formatdate
from io import BytesIO
from PIL import Image, ImageDraw, ImageOps
from secrets import token_hex
from sqlalchemy import and_
from sqlalchemy.future import select
from tornado.ioloop import IOLoop

from ..models import User


logger = logging.getLogger(__name__)


class UserMixin():

    async def authenticate(self, message):
        if 'payload' in message and 'email' in message['payload'] and 'remember' in message['payload']:
            if 'token' in message['payload']:
                async with self.sessionmaker() as session:
                    logger.debug(f'Logging in user {message["payload"]["email"]}')
                    query = select(User).filter(and_(User.email == message['payload']['email'],
                                                     User.token == message['payload']['token']))
                    result = await session.execute(query)
                    user = result.scalars().first()
                    if user:
                        self.user = user
                        await self.send_message({
                            'type': 'authenticated',
                            'payload': {
                                'email': message['payload']['email'],
                                'remember': message['payload']['remember'],
                                'token': message['payload']['token'],
                            }
                        })
                        self.user_mqtt_task = asyncio.create_task(self.on_mqtt_messages(f'user/{self.user.id}/+'))
                        return
            else:
                async with self.sessionmaker() as session:
                    logger.debug(f'Finding user {message["payload"]["email"]}')
                    query = select(User).filter(User.email == message['payload']['email'])
                    result = await session.execute(query)
                    user = result.scalars().first()
                    if user:
                        logger.debug(f'Generating and e-mailing login token')
                        user.token = token_hex(64)
                        await session.commit()

                        email = EmailMessage()
                        email.set_content(f'''Hello {user.name},

Click on the following link or copy it into your browser to log into the Senior Common Room:

{self.config['server']['base_url']}/frontend/?email={user.email}&token={user.token}&remember={str(message["payload"]["remember"])}

This e-mail is automatically generated. Please do not reply to it.
''')
                        email['Subject'] = 'Senior Common Room Login'
                        email['From'] = self.config['email']['from']
                        email['To'] = user.email
                        email['Date'] = formatdate()
                        smtp = smtplib.SMTP(self.config['email']['server'])
                        if self.config['email']['secure']:
                            smtp.starttls()
                        if self.config['email']['authentication']:
                            smtp.login(self.config['email']['authentication']['username'],
                                       self.config['email']['authentication']['password'])
                        smtp.send_message(email)
                        smtp.quit()

                        logger.debug(f'/frontend/?email={message["payload"]["email"]}&token={user.token}')
                        await self.send_message({
                            'type': 'authentication-token-sent'
                        })
                        return
        await self.send_message({
            'type': 'authentication-failed',
            'payload': {
                'email': 'E-mail address or Login Token invalid',
            }
        })

    async def get_user(self, message):
        if self.user is None or self.user.avatar is None \
                or not os.path.exists(os.path.join(self.config['storage']['avatars'],
                                                   f'{self.user.avatar}-large.png')) \
                or not os.path.exists(os.path.join(self.config['storage']['avatars'],
                                                   f'{self.user.avatar}-small.png')):
            await self.send_message({
                'type': 'onboarding-required'
            })
        else:
            await self.send_message({
                'type': 'user',
                'payload': {
                    'id': self.user.id,
                    'name': self.user.name,
                    'email': self.user.email,
                    'avatar': f'{self.config["server"]["prefixes"]["avatars"]}/{self.user.avatar}',
                    'roles': self.user.roles,
                    'blocked_users': self.user.blocked_users,
                }
            })

    async def update_user_profile(self, message):
        async with self.sessionmaker() as session:
            session.add(self.user)
            if 'name' in message['payload']:
                self.user.name = message['payload']['name']
            if 'email' in message['payload']:
                self.user.email = message['payload']['email']
            if 'roles' in message['payload']:
                new_roles = []
                if 'admin' in self.user.roles:
                    new_roles.append('admin')
                new_roles.extend([role for role in message['payload']['roles']
                                  if role != 'admin'])
                self.user.roles = new_roles
            await session.commit()
        await self.get_user(None)

    async def update_avatar_image(self, message):
        logger.debug('Updating the avatar image')
        if message['payload']['imageData'].startswith('data:'):
            message = message['payload']['imageData'][5:]
            filetype, b64data = message.split(';')
            if filetype in ['image/png', 'image/jpeg']:
                if b64data.startswith('base64,'):
                    b64data = b64data[7:]
                if os.path.exists(os.path.join(self.config['storage']['avatars'], f'{self.user.avatar}-large.png')):
                    os.unlink(os.path.join(self.config['storage']['avatars'], f'{self.user.avatar}-large.png'))
                if os.path.exists(os.path.join(self.config['storage']['avatars'], f'{self.user.avatar}-small.png')):
                    os.unlink(os.path.join(self.config['storage']['avatars'], f'{self.user.avatar}-small.png'))
                buffer = BytesIO(b64decode(b64data))
                if filetype == 'image/png':
                    format = 'PNG'
                elif filetype == 'image/jpeg':
                    format = 'JPEG'
                img = Image.open(buffer, formats=[format])
                if img.size[0] != img.size[1]:
                    if img.size[0] < img.size[1]:
                        img = ImageOps.fit(img, (img.size[0], img.size[0]), centering=(0.5, 0.5))
                    else:
                        img = ImageOps.fit(img, (img.size[1], img.size[1]), centering=(0.5, 0.5))
                mask = Image.new('L', img.size, 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0) + img.size, fill=255)
                img.putalpha(mask)
                updated = False
                suffix = ''
                while not updated:
                    try:
                        async with self.sessionmaker() as session:
                            session.add(self.user)
                            self.user.avatar = token_hex(16)
                            await session.commit()
                            updated = True
                    except Exception as e:
                        pass
                os.makedirs(self.config['storage']['avatars'], exist_ok=True)
                with open(os.path.join(self.config['storage']['avatars'], f'{self.user.avatar}-large.png'), 'wb') as out_f:
                    img.save(out_f, format='PNG')
                with open(os.path.join(self.config['storage']['avatars'], f'{self.user.avatar}-small.png'), 'wb') as out_f:
                    img.thumbnail((48, 48))
                    img.save(out_f, format='PNG')
                await self.send_message({
                    'type': 'avatar-image-updated'
                })
                logger.debug('Avatar image updated')
                return
        await self.send_message({
            'type': 'avatar-image-update-failed'
        })

    async def block_user(self, message):
        async with self.sessionmaker() as session:
            session.add(self.user)
            if self.user.blocked_users is None:
                self.user.blocked_users = [message['payload']['user']['id']]
            elif message['payload']['user']['id'] not in self.user.blocked_users:
                self.user.blocked_users.append(message['payload']['user']['id'])
            await session.commit()
        await self.get_user(None)

    async def unblock_user(self, message):
        async with self.sessionmaker() as session:
            session.add(self.user)
            if self.user.blocked_users and message['payload']['user']['id'] in self.user.blocked_users:
                self.user.blocked_users.remove(message['payload']['user']['id'])
            await session.commit()
        await self.get_user(None)
