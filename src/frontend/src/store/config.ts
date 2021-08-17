import { writable, get } from "svelte/store";
import { navigate } from 'svelte-navigator';

import { messages, sendMessage } from './connection';

export const coreConfig = writable({'title': 'The Senior Common Room'} as CoreConfigPayload);
export const rooms = writable([] as RoomConfigPayload[]);
export const badges = writable([] as BadgeConfigPayload[]);
export const timezones = writable([] as string[]);
export const schedule = writable([] as ScheduleConfigPayload[]);

messages.subscribe((message) => {
    if (message.type === 'authenticated') {
        sendMessage({
            type: 'get-rooms-config'
        });
        sendMessage({
            type: 'get-badges-config'
        });
        sendMessage({
            type: 'get-timezones-config'
        });
        sendMessage({
            type: 'get-schedule-config'
        });
    } else if (message.type === 'core-config') {
        coreConfig.set(message.payload as CoreConfigPayload);
        document.title = (message.payload as CoreConfigPayload).title;
    } else if (message.type === 'rooms-config') {
        const pathElements = window.location.pathname.split('/');
        let redirect = true;
        if (pathElements.length > 0) {
            if (pathElements[pathElements.length - 1] === 'profile' || pathElements[pathElements.length - 1] === 'schedule') {
                redirect = false;
            } else {
                (message.payload as RoomConfigPayload[]).forEach((room) => {
                    if (room.slug == pathElements[pathElements.length - 1]) {
                        redirect = false;
                    }
                });
            }
        }
        rooms.set(message.payload as RoomConfigPayload[]);
        if (redirect && (message.payload as RoomConfigPayload[]).length > 0) {
            navigate('/frontend/room/' + (message.payload as RoomConfigPayload[])[0].slug);
        }
    } else if (message.type === 'badges-config') {
        badges.set(message.payload as BadgeConfigPayload[]);
    } else if (message.type === 'timezones-config') {
        timezones.set((message.payload as TimezonesConfigPayload).timezones);
    } else if (message.type === 'schedule-config') {
        schedule.set(message.payload as ScheduleConfigPayload[])
    }
});
