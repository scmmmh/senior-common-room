import { createStore } from 'vuex';

import { localLoadValue, localStoreValue, localDeleteValue } from '../util/storage';

export const NOT_READY = 0;
export const BUSY = 1;
export const READY = 2;

interface State {
    connection: ConnectionState;
    user: UserState;
    publicRooms: string[];
    rooms: RoomListState;
    users: RoomUsersState;
    messages: MessageState[];
}

interface ConnectionState {
    state: 0 | 1 | 2;
    websocket: WebSocket | null;
    reconnectTimeout: number;
}

interface UserState {
    state: 0 | 1 | 2;
    id: string;
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
    id: string;
    email: string;
    name: string;
    accessToken: string;
}

interface RoomListState {
    [x: string]: RoomState;
}

export interface RoomState {
    id: string;
    label: string;
    lobby: boolean;
}

interface RoomUsersState {
    [x: string]: RoomUserState;
}

export interface RoomUserState {
    id: string;
    name: string;
}

export interface MessageState {
    user: RoomUserState;
    message: string;
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
            id: '',
            email: '',
            name: '',
            accessToken: '',
        },
        publicRooms: [],
        rooms: {},
        users: {},
        messages: [],
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
                state.user.id = payload.id;
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
        },

        setPublicRooms(state, payload: WebSocketMessage) {
            state.publicRooms = [];
            payload.rooms.forEach((room: RoomState) => {
                state.rooms[room.id] = room;
                state.publicRooms.push(room.id);
            })
        },

        setRoomUsers(state, payload: WebSocketMessage) {
            const users = {} as RoomUsersState;
            payload.users.forEach((user: RoomUserState) => {
                users[user.id] = user;
            });
            state.users = users;
        },

        addRoomUser(state, payload: WebSocketMessage) {
            if (payload.data.id !== state.user.id) {
                state.users[payload.data.id] = payload.data;
            }
        },

        removeRoomUser(state, payload: WebSocketMessage) {
            if (state.users[payload.data.id]) {
                delete state.users[payload.data.id];
            }
        },

        clearMessages(state) {
            state.messages = [];
        },

        addMessage(state, payload: MessageState) {
            state.messages.push(payload);
        },
    },

    actions: {
        async init({ dispatch }) {
            dispatch('connect');
        },

        connect({ state, commit, dispatch }) {
            return new Promise((resolve, reject) => {
                console.log(state.connection.state);
                if (state.connection.state === NOT_READY) {
                    const websocket = new WebSocket('ws://localhost:6543/websocket');
                    websocket.addEventListener('open', () => {
                        commit('setConnectionState', READY);
                        commit('setWebSocket', websocket);
                        resolve(true);
                    });
                    websocket.addEventListener('message', (ev) => {
                        dispatch('receiveMessage', JSON.parse(ev.data));
                    });
                    websocket.addEventListener('close', () => {
                        commit('setConnectionState', NOT_READY);
                        dispatch('disconnect');
                        dispatch('reconnect');
                    });
                    websocket.addEventListener('error', () => {
                        commit('setConnectionState', NOT_READY);
                        dispatch('disconnect');
                        dispatch('reconnect');
                        reject();
                    });
                } else if (state.connection.state === BUSY) {
                    commit('setConnectionState', BUSY);
                } else if (state.connection.state === READY) {
                    resolve(true);
                }
            });
        },

        async disconnect({ commit }) {
            commit('setConnectionState', NOT_READY);
            commit('setWebSocket', null);
        },

        async reconnect({ state, commit, dispatch }) {
            clearTimeout(state.connection.reconnectTimeout);
            commit('setReconnectTimeout', setTimeout(() => {
                dispatch('connect');
            }, 5000));
        },

        async sendMessage({ state, dispatch }, payload: any) {
            await dispatch('connect');
            if (state.connection.websocket) {
                state.connection.websocket.send(JSON.stringify(payload));
            }
        },

        async receiveMessage({ dispatch, commit }, payload: WebSocketMessage) {
            if (payload.type === 'authenticate') {
                dispatch('authenticate');
            } else if (payload.type === 'authenticated') {
                dispatch('authenticated', payload);
            } else if (payload.type === 'authenticationFailed') {
                dispatch('authenticationFailed');
            } else if (payload.type === 'publicRoomsList') {
                commit('setPublicRooms', payload);
            } else if (payload.type === 'roomUsersList') {
                commit('setRoomUsers', payload);
            } else if (payload.type === 'userEntersRoom') {
                commit('addRoomUser', payload);
                commit('addMessage', {
                    user: payload.data,
                    message: 'Has entered the room',
                });
            } else if (payload.type === 'userLeavesRoom') {
                commit('removeRoomUser', payload);
                commit('addMessage', {
                    user: payload.data,
                    message: 'Has left the room',
                });
            } else {
                console.log(payload);
            }
        },

        async enterRoom({ dispatch }, payload: string) {
            await dispatch('sendMessage', {
                type: 'enterRoom',
                data: {
                    room: payload,
                },
            });
        },

        async leaveRoom({ dispatch }, payload: string) {
            await dispatch('sendMessage', {
                type: 'leaveRoom',
                data: {
                    room: payload,
                },
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
                    data: {
                        email: email,
                        accessToken: accessToken,
                    },
                });
            }
        },

        async authenticateEmailPassword({ dispatch, commit }, payload: LoginDetails) {
            commit('setUserState', BUSY);
            dispatch('sendMessage', {
                type: 'authenticate',
                data: {
                    email: payload.email,
                    password: payload.password,
                },
            });
        },

        async authenticationFailed({ commit}) {
            localDeleteValue('user.accessToken');
            commit('setUserState', NOT_READY);
            commit('setUser', null);
        },

        async authenticated({ commit, dispatch }, payload: WebSocketMessage) {
            commit('setUser', {
                id: payload.data.id,
                email: payload.data.email,
                name: payload.data.name,
                accessToken: payload.data.accessToken,
            });
            commit('setUserState', READY);
            await dispatch('sendMessage', {type: 'getPublicRooms'});
        },

        async logout({ commit, dispatch }) {
            dispatch('sendMessage', {
                type: 'logout',
            });
            commit('setUser', null);
            commit('setUserState', 0);
            localDeleteValue('user.accessToken');
        },
    },
    modules: {
    }
})
