import logging

from pytz import timezone, common_timezones


logger = logging.getLogger(__name__)


class ConfigMixin():

    async def get_rooms_config(self):
        await self.send_message({
            'type': 'rooms-config',
            'payload': self.config['rooms']
        })

    async def get_badges_config(self):
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

    async def get_schedule_config(self):
        tz = timezone('UTC')
        try:
            tz = timezone(self.user.timezone)
        except:
            pass
        def localise_schedule_entry(entry):
            start = entry['start'].astimezone(tz)
            end = entry['end'].astimezone(tz)
            return {
                'title': entry['title'],
                'start_date': start.strftime('%d %B %Y'),
                'start_time': start.strftime('%H:%M %Z'),
                'end_date': end.strftime('%d %B %Y'),
                'end_time': end.strftime('%H:%M %Z'),
                'day_diff': (end - start).days + 1 if start.year != end.year or start.month != end.month or start.day != end.day else 0,
                'room': entry['room'],
                'description': entry['description']
            }

        if 'schedule' in self.config:
            await self.send_message({
                'type': 'schedule-config',
                'payload': [localise_schedule_entry(entry) for entry in self.config['schedule']]
            })
        else:
            await self.send_message({
                'type': 'schedule-config',
                'payload': []
            })

    async def get_timezones_config(self):
        await self.send_message({
            'type': 'timezones-config',
            'payload': {
                'timezones': common_timezones
            }
        })
