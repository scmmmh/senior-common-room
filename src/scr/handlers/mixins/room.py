class RoomMixin():

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

    async def list_room_participants(self, room_name):
        self.send_message({'type': 'room_participants_list', 'data': []})
