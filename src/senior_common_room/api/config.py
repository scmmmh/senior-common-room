import logging


logger = logging.getLogger(__name__)


class ConfigMixin():

    async def get_rooms_config(self, message):
        await self.send_message({
            'type': 'rooms-config',
            'payload': self.config['rooms']
        })
