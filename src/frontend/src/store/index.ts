import { createStore } from 'vuex'

export default createStore({
    state: {
    },
    mutations: {
    },
    actions: {
        init({ state }) {
            const ws = new WebSocket('ws://localhost:6543/websocket');
            ws.addEventListener('open', () => {
                ws.send(JSON.stringify({'msg': 'Test'}));
            });
            ws.addEventListener('message', (ev) => {
                console.log(ev);
                ws.close();
            });
        },
    },
    modules: {
    }
});
