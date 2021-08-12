import { writable } from 'svelte/store';

import { sendMessage, messages } from './connection';

export const jitsiRoomUsers = writable([] as number[]);

messages.subscribe((message) => {
    if (message.type === 'authentication-required') {
        jitsiRoomUsers.set([]);
    } else if (message.type === 'open-jitsi-room') {
        jitsiRoomUsers.set([]);
        sendMessage({
            type: 'get-jitsi-room-users'
        });
    } else if (message.type === 'left-jitsi-room') {
        jitsiRoomUsers.set([]);
    } else if (message.type === 'jitsi-room-users') {
        jitsiRoomUsers.set((message.payload as JitsiRoomUsersPayload).users);
    }
})
