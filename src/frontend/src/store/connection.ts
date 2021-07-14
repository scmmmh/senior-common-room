import { writable, derived } from 'svelte/store';

const INITIAL = 0;
const CONNECTING = 1;
const CONNECTED = 2;
const RECONNECTING = 3;
const FAILED = 4;
const DISCONNECTED = 5;
const MAX_RECONNECT_ATTEMPTS = 8;

const connectionStatus = writable(INITIAL);
export const messages = writable({} as ApiMessage);
let connection = null;
let reconnectTimeout = -1;
let reconnectCount = MAX_RECONNECT_ATTEMPTS + 1;

export function connect() {
    if (connection === null) {
        clearTimeout(reconnectTimeout)
        if (reconnectCount === 6) {
            connectionStatus.set(CONNECTING);
        } else {
            connectionStatus.set(RECONNECTING);
        }
        if (window.location.protocol === 'https:') {
            connection = new WebSocket('wss://' + window.location.hostname + ':' + window.location.port + '/api');
        } else {
            connection = new WebSocket('ws://' + window.location.hostname + ':' + window.location.port + '/api');
        }
        connection.addEventListener('open', () => {
            reconnectCount = MAX_RECONNECT_ATTEMPTS + 1;
            connectionStatus.set(CONNECTED);
        });
        connection.addEventListener('close', () => {
            connection = null;
            reconnectCount = reconnectCount - 1;
            if (reconnectCount >= 0) {
                connectionStatus.set(DISCONNECTED);
                reconnectTimeout = window.setTimeout(() => {
                    connect();
                }, Math.pow(MAX_RECONNECT_ATTEMPTS - reconnectCount, 2) * 1000 + 50);
            } else {
                connectionStatus.set(FAILED);
            }
        });
        connection.addEventListener('message', (message) => {
            if (message.data) {
                messages.set(JSON.parse(message.data));
            }
        });
    }
}

export const isConnecting = derived(connectionStatus, (status) => {
    return status === CONNECTING;
});

export const isConnected = derived(connectionStatus, (status) => {
    return status === CONNECTED;
});

export const isReconnecting = derived(connectionStatus, (status) => {
    return status === RECONNECTING;
});

export const isFailed = derived(connectionStatus, (status) => {
    return status === FAILED;
});

export const isDisconnected = derived(connectionStatus, (status) => {
    return status === DISCONNECTED;
});

export function sendMessage(message: ApiMessage) {
    if (connection && connection.readyState === 1) {
        connection.send(JSON.stringify(message));
    }
}
