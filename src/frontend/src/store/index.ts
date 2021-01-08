import { createStore } from 'vuex';

import { localLoadValue, localStoreValue, localDeleteValue } from '../util/storage';

export const NOT_READY = 0;
export const BUSY = 1;
export const READY = 2;

interface State {
    connection: ConnectionState;
    user: UserState;
}

interface ConnectionState {
    state: 0 | 1 | 2;
    websocket: WebSocket | null;
    reconnectTimeout: number;
}

interface UserState {
    state: 0 | 1 | 2;
    email: string;
    name: string;
    accessToken: string;
}

interface WebSocketMessage {
    type: string;
    [x: string]: any;
}

export interface LoginDetails {
    email: string;
    password: string;
}

interface AuthenticatedMessage {
    email: string;
    name: string;
    accessToken: string;
}

export default createStore({
    state: {
        connection: {
            state: 0,
            websocket: null,
            reconnectTimeout: -1,
        },
        user: {
            state: 0,
            email: '',
            name: '',
            accessToken: '',
        }
    } as State,

    mutations: {
        setConnectionState(state, payload: 0 | 1 | 2) {
            state.connection.state = payload;
        },

        setWebSocket(state, payload: WebSocket | null) {
            state.connection.websocket = payload;
        },

        setReconnectTimeout(state, payload: number) {
            state.connection.reconnectTimeout = payload;
        },

        setUserState(state, payload: 0 | 1 | 2) {
            state.user.state = payload;
        },

        setUser(state, payload: AuthenticatedMessage | null) {
            if (payload) {
                state.user.email = payload.email;
                state.user.name = payload.name;
                state.user.accessToken = payload.accessToken;
                localStoreValue('user.email', payload.email);
                localStoreValue('user.accessToken', payload.accessToken);
            } else {
                state.user.email = '';
                state.user.name = '';
                state.user.accessToken = '';
            }
        }
    },

    actions: {
        async init({ dispatch }) {
            dispatch('connect');
        },

        connect({ state, commit, dispatch }) {
            return new Promise((resolve, reject) => {
                if (state.connection.state === 0) {
                    commit('setConnectionState', BUSY);
                    const websocket = new WebSocket('ws://localhost:6543/websocket');
                    websocket.addEventListener('open', () => {
                        commit('setConnectionState', READY);
                        commit('setWebSocket', websocket);
                        resolve();
                    });
                    websocket.addEventListener('message', (ev) => {
                        dispatch('receiveMessage', JSON.parse(ev.data));
                    });
                    websocket.addEventListener('close', () => {
                        commit('setConnectionState', NOT_READY);
                        dispatch('disconnect');
                    });
                    websocket.addEventListener('error', () => {
                        commit('setConnectionState', NOT_READY);
                        dispatch('disconnect');
                        dispatch('reconnect');
                        reject();
                    });
                } else if (state.connection.state === 1) {
                    commit('setConnectionState', BUSY);
                } else if (state.connection.state === 2) {
                    resolve();
                }
            });
        },

        async disconnect({ commit }) {
            commit('setConnectionState', 0);
            commit('setWebSocket', null);
        },

        async reconnect({ state, commit, dispatch }) {
            clearTimeout(state.connection.reconnectTimeout);
            commit('setConnectionState', BUSY);
            commit('setReconnectTimeout', setTimeout(() => {
                dispatch('connect');
            }, 10000));
        },

        async sendMessage({ state, dispatch }, payload: any) {
            await dispatch('connect');
            if (state.connection.websocket) {
                state.connection.websocket.send(JSON.stringify(payload));
            }
        },

        async receiveMessage({ dispatch }, payload: WebSocketMessage) {
            if (payload.type === 'authenticate') {
                dispatch('authenticate');
            } else if (payload.type === 'authenticated') {
                dispatch('authenticated', payload);
            } else if (payload.type === 'authenticationFailed') {
                dispatch('authenticationFailed');
            } else {
                console.log(payload);
            }
        },

        async enterRoom({ dispatch }, payload: string) {
            await dispatch('sendMessage', {
                type: 'enterRoom',
                room: payload,
            });
        },

        async leaveRoom({ dispatch }, payload: string) {
            await dispatch('sendMessage', {
                type: 'leaveRoom',
                room: payload,
            });
        },

        async authenticate({ commit, dispatch }) {
            commit('setUserState', NOT_READY);
            const email = localLoadValue('user.email', null);
            const accessToken = localLoadValue('user.accessToken', null);
            if (email && accessToken) {
                commit('setUserState', BUSY);
                commit('setUser', null);
                dispatch('sendMessage', {
                    type: 'authenticate',
                    email: email,
                    accessToken: accessToken,
                });
            }
        },

        async authenticateEmailPassword({ dispatch, commit }, payload: LoginDetails) {
            commit('setUserState', BUSY);
            dispatch('sendMessage', {
                type: 'authenticate',
                email: payload.email,
                password: payload.password,
            });
        },

        async authenticationFailed({ commit}) {
            localDeleteValue('user.accessToken');
            commit('setUserState', NOT_READY);
            commit('setUser', null);
        },

        async authenticated({ commit }, payload: WebSocketMessage) {
            commit('setUser', {
                email: payload.email,
                name: payload.name,
                accessToken: payload.accessToken,
            });
            commit('setUserState', READY);
        },
    },
    modules: {
    }
})
