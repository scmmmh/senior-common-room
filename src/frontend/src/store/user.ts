import { writable, derived } from "svelte/store";

import { messages, sendMessage } from './connection';

export const user = writable(null as UserPayload);
const STARTUP = 0;
const ONBOARDING = 1;
const ONBOARDED = 2;
const onboardingState = writable(STARTUP);

messages.subscribe((message) => {
    if (message.type === 'authenticated') {
        sendMessage({
            type: 'get-user'
        });
        onboardingState.set(STARTUP);
    } else if (message.type === 'onboarding-required') {
        onboardingState.set(ONBOARDING);
    } else if (message.type === 'user') {
        onboardingState.set(ONBOARDED);
        user.set(message.payload as UserPayload);
    }
});

export const isOnboarded = derived(onboardingState, (state) => {
    return state === ONBOARDED
});

export const isOnboarding = derived(onboardingState, (state) => {
    return state === ONBOARDING;
});
