<template>
    <div role="alert" aria-modal="true" class="show-for-small">
        <div>
            <h2>Display unsupported</h2>
            <p>Unfortunately the Senior Common Room currently requires a screen at least 1024x768 pixel in size.</p>
        </div>
    </div>
    <div v-if="!isConnected" role="dialog" aria-modal="true" class="hide-for-small">
        <div>
            <h2>Connecting...</h2>
            <p>You are being connected to the Senior Common Room. Please wait...</p>
        </div>
    </div>
    <main id="application" v-else class="hide-for-small">
        <nav>
            <ul role="menubar">
                <aria-menu-item v-for="room in publicRooms" :key="room.id" @click="navigate({'name': 'room', 'params': {'rid': room.id}})" :current="$route.name === 'room' && $route.params.rid === room.id" tabindex="0">Senior Common Room</aria-menu-item>
                <aria-menu-item @click="navigate({name: 'about'})" :current="$route.name === 'about'">About</aria-menu-item>
            </ul>
        </nav>
        <login v-if="!isAuthenticated"/>
        <router-view v-else/>
    </main>
</template>

<script lang="ts">
import { Options } from 'vue-class-component';

import { ComponentRoot } from './base';
import { READY } from './store/index';
import Login from './components/Login.vue';
import AriaMenuItem from './components/aria/AriaMenuItem.vue';


@Options({
    components: {
        Login,
        AriaMenuItem,
    }
})
export default class App extends ComponentRoot {

    public get isConnected() {
        return this.$store.state.connection.state === READY;
    }

    public get isAuthenticated() {
        return this.$store.state.user.state === READY;
    }

    public get publicRooms() {
        return this.$store.state.publicRooms.map((roomId) => {
            const room = this.$store.state.rooms[roomId];
            if (room) {
                return room;
            } else {
                return null;
            }
        }).filter((room) => {
            return room != null;
        });
    }

    public mounted() {
        this.$store.dispatch('init');
    }

    public unmounted() {
        this.$store.dispatch('close');
    }

    public navigate(route: {name: string; params: {rid: string}}) {
        this.$router.push(route);
    }
}
</script>
