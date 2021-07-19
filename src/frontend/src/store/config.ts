import { writable, get } from "svelte/store";
import { navigate } from 'svelte-navigator';

import { messages, sendMessage } from './connection';

export const rooms = writable([] as RoomConfigPayload[]);

messages.subscribe((message) => {
    if (message.type === 'authenticated') {
        sendMessage({
            type: 'get-rooms-config'
        });
    } else if (message.type === 'rooms-config') {
        const firstLoad = (get(rooms).length === 0);
        rooms.set(message.payload as RoomConfigPayload[]);
        if (firstLoad && (message.payload as RoomConfigPayload[]).length > 0) {
            navigate('/frontend/room/' + (message.payload as RoomConfigPayload[])[0].slug);
        }
    }
});
