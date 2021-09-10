import { writable } from 'svelte/store';

import { executeAction } from './action';
import { sendMessage, messages } from './connection';

export const overlay = writable(null);

executeAction.subscribe((action) => {
    if (action) {
        if (action.action === 'showIframe' && action.url) {
            overlay.set({
                type: 'iframe',
                url: action.url,
            });
        } else if (action.action === 'showJitsiCall' && action.roomName) {
            sendMessage({
                type: 'enter-jitsi-room',
                payload: {
                    name: action.roomName,
                    subject: action.subject,
                }
            });
        }
    }
});

messages.subscribe((message) => {
    if (message.type === 'authentication-required') {
        overlay.set(null);
    } else if (message.type === 'open-jitsi-room') {
        overlay.set({
            type: 'jitsi-room',
            name: (message.payload as OpenJitsiRoomPayload).room_name,
            subject: (message.payload as OpenJitsiRoomPayload).subject,
            url: (message.payload as OpenJitsiRoomPayload).url,
            password: (message.payload as OpenJitsiRoomPayload).password,
            jwt: (message.payload as OpenJitsiRoomPayload).jwt,
        });
    }
})
