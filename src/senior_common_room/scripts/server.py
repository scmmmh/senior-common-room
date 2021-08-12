import asyncio
import asyncio_mqtt
import click
import json
import logging

from secrets import token_hex
from tornado.web import Application
from tornado.ioloop import IOLoop

from ..handlers import ApiHandler


logger = logging.getLogger(__name__)


async def jitsi_room_state_server(config):
    jitsi_rooms = {}
    logger.debug('Jitsi room state server starting up')
    async with asyncio_mqtt.Client(config['mosquitto']) as client:
        logger.debug('Jitsi room state server started')

        async def enter_handler():
            async with client.filtered_messages("jitsi-rooms/+/enter") as messages:
                await client.subscribe("jitsi-rooms/+/enter")
                async for message in messages:
                    payload = json.loads(message.payload.decode())
                    room_name = message.topic.split('/')[1]
                    if room_name == '_private':
                        room_name = token_hex(32)
                        while room_name in jitsi_rooms:
                            room_name = token_hex(32)
                        jitsi_rooms[room_name] = {
                            'url': token_hex(32),
                            'password': token_hex(32),
                            'users': payload['users'],
                            'subject': 'Private chat'
                        }
                        for user in payload['users']:
                            await client.publish(f'user/{user}/enter-jitsi-room',
                                                 payload=json.dumps({
                                                     'room_name': room_name,
                                                     'url': jitsi_rooms[room_name]['url'],
                                                     'password': jitsi_rooms[room_name]['password'],
                                                     'subject': jitsi_rooms[room_name]['subject']
                                                 }).encode())
                        await client.publish(f'jitsi-rooms/{room_name}/request-user-list')
                    else:
                        if room_name not in jitsi_rooms:
                            jitsi_rooms[room_name] = {
                                'url': token_hex(32),
                                'password': token_hex(32),
                                'users': [payload['user']],
                                'subject': payload['subject']
                            }
                        elif payload['user'] not in jitsi_rooms[room_name]['users']:
                            jitsi_rooms[room_name]['users'].append(payload['user'])
                        logger.debug(f'Entering jitsi room for user/{payload["user"]}/enter-jitsi-room')
                        await client.publish(f'user/{payload["user"]}/enter-jitsi-room',
                                             payload=json.dumps({
                                                 'room_name': room_name,
                                                 'url': jitsi_rooms[room_name]['url'],
                                                 'password': jitsi_rooms[room_name]['password'],
                                                 'subject': jitsi_rooms[room_name]['subject']
                                             }).encode())
                        await client.publish(f'jitsi-rooms/{room_name}/request-user-list')

        async def leave_handler():
            async with client.filtered_messages("jitsi-rooms/+/leave") as messages:
                await client.subscribe("jitsi-rooms/+/leave")
                async for message in messages:
                    payload = json.loads(message.payload.decode())
                    room_name = message.topic.split('/')[1]
                    if room_name in jitsi_rooms:
                        if payload['user'] in jitsi_rooms[room_name]['users']:
                            jitsi_rooms[room_name]['users'].remove(payload['user'])
                            logger.debug(f'User {payload["user"]} leaving {room_name}')
                            await client.publish(f'user/{payload["user"]}/leave_jitsi_room')
                            await client.publish(f'jitsi-rooms/{room_name}/request-user-list')
                        if len(jitsi_rooms[room_name]['users']) == 0:
                            del jitsi_rooms[room_name]

        async def request_user_list_handler():
            async with client.filtered_messages("jitsi-rooms/+/request-user-list") as messages:
                await client.subscribe("jitsi-rooms/+/request-user-list")
                async for message in messages:
                    room_name = message.topic.split('/')[1]
                    if room_name in jitsi_rooms:
                        await client.publish(f'jitsi-rooms/{room_name}/user-list',
                                             payload=json.dumps({'users': jitsi_rooms[room_name]['users']}).encode())

        await asyncio.gather(enter_handler(), leave_handler(), request_user_list_handler())


@click.command()
@click.pass_context
def server(ctx):
    logger.info('Server starting up')
    app = Application([
        (r'/api', ApiHandler, {'config': ctx.obj['config']}),
    ], debug=True)
    app.listen(6543, '0.0.0.0')
    if 'jitsi' in ctx.obj['config']:
        IOLoop.current().add_callback(jitsi_room_state_server, ctx.obj['config'])
    IOLoop.current().start()
