import { writable, derived } from "svelte/store";

import { messages } from './connection';

export const action = writable(null);

export const executeAction = writable(null);

export const actionLabel = derived(action, (action) => {
    if (action) {
        if (action.label) {
            return action.label;
        } else if (action.action === 'logout') {
            return 'Logout';
        } else if (action.action === 'switchRoom') {
            return 'Switch to room';
        } else if (action.action === 'showJitsiCall') {
            return 'Start chatting';
        } else if (action.action === 'showIframe') {
            return 'View some content';
        } else {
            console.log(action);
        }
    } else {
        return '';
    }
});

messages.subscribe((message) => {
    if (message.type === 'authentication-required') {
        action.set(null);
    }
});
