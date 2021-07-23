import { writable, derived } from 'svelte/store';

import { messages, sendMessage } from './connection';
import { executeAction } from './action';
import { localStoreValue, localLoadValue, localDeleteValue, sessionStoreValue, sessionLoadValue, sessionDeleteValue, NestedStorage } from '../storage';

const NOT_AUTHENTICATED = 0;
const AUTHENTICATION_REQUIRED = 1;
const AUTHENTICATING = 2;
const AUTHENTICATION_TOKEN_SENT = 3;
const AUTHENTICATED = 4;
const AUTHENTICATION_FAILED = 5;

const authenticationStatus = writable(NOT_AUTHENTICATED);

messages.subscribe((data) => {
    if (data.type === 'authentication-required') {
        const params = new URLSearchParams(window.location.search);
        if (params.has('email') && params.has('token')) {
            authenticationStatus.set(AUTHENTICATING);
            sendMessage({
                type: 'authenticate',
                payload: {
                    email: params.get('email'),
                    remember: params.get('remember').toLowerCase() === 'true',
                    token: params.get('token'),
                }
            });
        } else if (localLoadValue('authentication', null)) {
            const auth = localLoadValue('authentication', null) as NestedStorage;
            authenticationStatus.set(AUTHENTICATING);
            sendMessage({
                type: 'authenticate',
                payload: {
                    email: auth.email as string,
                    remember: true,
                    token: auth.token as string,
                }
            });
        } else if (sessionLoadValue('authentication', null)) {
            const auth = sessionLoadValue('authentication', null) as NestedStorage;
            authenticationStatus.set(AUTHENTICATING);
            sendMessage({
                type: 'authenticate',
                payload: {
                    email: auth.email as string,
                    remember: false,
                    token: auth.token as string,
                }
            });
        } else {
            authenticationStatus.set(AUTHENTICATION_REQUIRED);
        }
    } else if (data.type === 'authentication-token-sent') {
        authenticationStatus.set(AUTHENTICATION_TOKEN_SENT);
    } else if (data.type === 'authenticated') {
        authenticationStatus.set(AUTHENTICATED);
        if (data.payload) {
            if ((data.payload as AuthenticatePayload).remember) {
                localStoreValue('authentication', data.payload as unknown as NestedStorage);
            } else {
                sessionStoreValue('authentication', data.payload as unknown as NestedStorage);
            }
            if (window.location.search) {
                window.location.search = '';
            }
        }
    } else if (data.type === 'authentication-failed') {
        authenticationStatus.set(AUTHENTICATION_FAILED);
    }
});

executeAction.subscribe((action) => {
    if (action) {
        if (action.action === 'logout') {
            localDeleteValue('authentication');
            sessionDeleteValue('authentication');
            window.location.reload();
        }
    }
});

export function authenticate(email: string, remember: boolean) {
    authenticationStatus.set(AUTHENTICATING);
    sendMessage({
        type: 'authenticate',
        payload: {
            email: email,
            remember: remember,
        },
    });
}

export const isAuthenticationRequired = derived(authenticationStatus, (status) => {
    return status === AUTHENTICATION_REQUIRED;
});

export const isAuthenticating = derived(authenticationStatus, (status) => {
    return status === AUTHENTICATING;
});

export const isAuthenticationTokenSent = derived(authenticationStatus, (status) => {
    return status === AUTHENTICATION_TOKEN_SENT;
});

export const isAuthenticated = derived(authenticationStatus, (status) => {
    return status === AUTHENTICATED;
});

export const isAuthenticationFailed = derived(authenticationStatus, (status) => {
    return status === AUTHENTICATION_FAILED;
});
