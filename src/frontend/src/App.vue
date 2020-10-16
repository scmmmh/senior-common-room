<template>
    <div v-if="!isConnected" role="dialog" aria-modal="true">
        <div>
            <h2>Connecting...</h2>
            <p>You are being connected to the Senior Common Room. Please wait...</p>
        </div>
    </div>
    <main id="application" v-else>
        <nav>
            <ul role="menubar">
                <aria-menu-item @click="navigate('lobby')" :current="$route.name === 'lobby'" tabindex="0">Senior Common Room</aria-menu-item>
                <aria-menu-item @click="navigate('about')" :current="$route.name === 'about'">About</aria-menu-item>
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

    public mounted() {
        this.$store.dispatch('init');
    }

    public unmounted() {
        this.$store.dispatch('close');
    }

    public navigate(routeName: string) {
        this.$router.push({name: routeName});
    }
}
</script>
