<template>
    <div v-if="!isConnected">
        <h2>Connecting...</h2>
    </div>
    <div v-else>
        <nav>
            <ul role="menubar">
                <li role="presentation">
                    <a role="menuitem">Lobby</a>
                </li>
            </ul>
        </nav>
        <div id="nav">
            <router-link to="/">Home</router-link> |
            <router-link to="/about">About</router-link>
        </div>
        <login v-if="!isAuthenticated"/>
        <router-view v-else/>
    </div>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';

import { READY } from './store/index';
import Login from './components/Login.vue';

@Options({
    components: {
        Login
    }
})
export default class App extends Vue {

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
}
</script>
