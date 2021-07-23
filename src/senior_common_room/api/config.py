import logging


logger = logging.getLogger(__name__)


class ConfigMixin():

    async def get_rooms_config(self, message):
        await self.send_message({
            'type': 'rooms-config',
            'payload': self.config['rooms']
        })

    async def get_badges_config(self, message):
        if 'badges' in self.config:
            await self.send_message({
                'type': 'badges-config',
                'payload': self.config['badges']
            })
        else:
            await self.send_message({
                'type': 'badges-config',
                'payload': []
            })
