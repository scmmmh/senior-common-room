import asyncio_mqtt
import logging
import json

from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler

from .api.config import ConfigMixin
from .api.jitsi import JitsiMixin
from .api.user import UserMixin
from .api.room import RoomMixin
from .api.messages import MessagesMixin
from .models import create_sessionmaker


logger = logging.getLogger(__name__)


class ApiHandler(WebSocketHandler, ConfigMixin, JitsiMixin, UserMixin, RoomMixin, MessagesMixin):

    def initialize(self, config):
        self.config = config
        self.sessionmaker = create_sessionmaker(config['database']['dsn'])
        self.mqtt = asyncio_mqtt.Client(hostname=config['mosquitto'], port=1883)
        self.user = None
        self.user_mqtt_task = None
        self.room_mqtt_task = None
        logger.debug('Initialised')

    async def open(self):
        logger.debug('Opening websocket connection')
        await self.mqtt.connect(timeout=5)
        await self.send_message({'type': 'authentication-required'})
        await self.setup_messages_task()
        logger.debug('Websocket connection opened')

    def on_close(self):
        logger.debug('Websocket connection closed')
        IOLoop.current().add_callback(self.jitsi_shutdown)
        if self.user_mqtt_task:
            self.user_mqtt_task.cancel()
        if self.room_mqtt_task:
            self.room_mqtt_task.cancel()
        self.teardown_messages_task()
        IOLoop.current().add_callback(self.teardown_room)
        IOLoop.current().add_callback(self.mqtt.disconnect)

    async def on_mqtt_messages(self, topic):
        logger.debug(f'Listening to mqtt messages on {topic}')
        async with self.mqtt.filtered_messages(topic) as messages:
            await self.mqtt.subscribe(topic)
            async for message in messages:
                if message.topic == f'user/{self.user.id}/enter-jitsi-room' and 'jitsi' in self.config:
                    await self.enter_jitsi_room(json.loads(message.payload.decode()))
                elif message.topic.startswith('room/') and message.topic.endswith('/set-avatar-location'):
                    await self.room_update_avatar_location(json.loads(message.payload.decode()))
                elif message.topic.startswith('room/') and message.topic.endswith('/leave'):
                    await self.room_remove_avatar(json.loads(message.payload.decode()))
                elif message.topic.startswith('messages/'):
                    await self.receive_broadcast_message(json.loads(message.payload.decode()))
                elif message.topic == f'user/{self.user.id}/message':
                    await self.receive_user_message(json.loads(message.payload.decode()))
                elif message.topic == f'user/{self.user.id}/request-video-chat':
                    await self.receive_request_video_chat_message(json.loads(message.payload.decode()))
                elif self.jitsi_room_name and message.topic == f'jitsi-rooms/{self.jitsi_room_name}/user-list':
                    await self.jitsi_room_user_list(json.loads(message.payload.decode()))
                elif self.jitsi_room_name and message.topic == f'user/{self.user.id}/leave_jitsi_room':
                    await self.leave_jitsi_room()
                elif message.topic == f'user/{self.user.id}/reconnect':
                    self.close()
                else:
                    logger.debug(message.topic)

    async def on_message(self, data):
        try:
            message = json.loads(data)
            if 'type' in message:
                if message['type'] == 'authenticate':
                    await self.authenticate(message)
                elif message['type'] == 'get-core-config':
                    await self.get_core_config()
                elif message['type'] == 'get-rooms-config':
                    await self.get_rooms_config()
                elif message['type'] == 'get-badges-config':
                    await self.get_badges_config()
                elif message['type'] == 'get-timezones-config':
                    await self.get_timezones_config()
                elif message['type'] == 'get-schedule-config':
                    await self.get_schedule_config()
                elif message['type'] == 'get-user':
                    await self.get_user(message)
                elif message['type'] == 'update-user-profile':
                    await self.update_user_profile(message)
                elif message['type'] == 'update-avatar-image':
                    await self.update_avatar_image(message)
                elif message['type'] == 'enter-jitsi-room' and 'jitsi' in self.config:
                    await self.request_jitsi_room(message)
                elif message['type'] == 'leave-jitsi-room' and 'jitsi' in self.config:
                    await self.leave_jitsi_room()
                elif message['type'] == 'get-jitsi-room-users' and 'jitsi' in self.config:
                    await self.request_jitsi_room_users()
                elif message['type'] == 'enter-room':
                    await self.enter_room(message)
                elif message['type'] == 'set-avatar-location':
                    await self.room_set_avatar_location(message)
                elif message['type'] == 'leave-room':
                    await self.leave_room(message)
                elif message['type'] == 'broadcast-message':
                    await self.send_broadcast_message(message)
                elif message['type'] == 'user-message':
                    await self.send_user_message(message)
                elif message['type'] == 'request-video-chat-message':
                    await self.send_request_video_chat_message(message)
                elif message['type'] == 'request-join-video-chat-message':
                    await self.send_request_join_video_chat_message(message)
                elif message['type'] == 'accept-video-chat-message':
                    await self.send_accept_video_chat_message(message)
                elif message['type'] == 'block-user':
                    await self.block_user(message)
                elif message['type'] == 'unblock-user':
                    await self.unblock_user(message)
                else:
                    logger.debug(data)
            else:
                logger.debug(data)
        except Exception as e:
            logger.error(e)


    async def send_message(self, msg):
        await self.write_message(json.dumps(msg))

    async def send_mqtt_message(self, topic, msg=None):
        if msg:
            await self.mqtt.publish(topic, payload=json.dumps(msg).encode())
        else:
            await self.mqtt.publish(topic)

    def check_origin(self, *args, **kwargs):
        # TODO: Enable only in dev mode
        return True
