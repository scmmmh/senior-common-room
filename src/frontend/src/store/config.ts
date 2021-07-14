import { writable } from "svelte/store";

import { messages, sendMessage } from './connection';

export const rooms = writable([] as RoomConfigPayload[]);

messages.subscribe((message) => {
    if (message.type === 'authenticated') {
        sendMessage({
            type: 'get-rooms-config'
        });
    } else if (message.type === 'rooms-config') {
        rooms.set(message.payload as RoomConfigPayload[]);
    }
});
