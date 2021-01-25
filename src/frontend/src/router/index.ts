import { createRouter, createWebHashHistory, RouteRecordRaw } from 'vue-router'
const routes: Array<RouteRecordRaw> = [
    {
        path: '/',
        name: 'lobby',
        component: () => import(/* webpackChunkName: "lobby" */ '../views/Lobby.vue'),
    },
    {
        path: '/room/:rid',
        name: 'room',
        component: () => import(/* webpackChunkName: "lobby" */ '../views/Room.vue'),
    },
    {
        path: '/about',
        name: 'about',
        // route level code-splitting
        // this generates a separate chunk (about.[hash].js) for this route
        // which is lazy-loaded when the route is visited.
        component: () => import(/* webpackChunkName: "about" */ '../views/About.vue'),
    },
]

const router = createRouter({
    history: createWebHashHistory(),
    routes,
})

export default router;
