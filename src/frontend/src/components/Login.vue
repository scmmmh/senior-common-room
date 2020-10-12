<template>
    <div role="popup" id="login">
        <h1>Senior Common Room - Login</h1>
        <p v-if="isAuthenticating">Authentication in progress...</p>
        <form v-else @submit="login">
            <label>E-Mail
                <input type="email" v-model="email"/>
                <span v-if="attempted" class="error">E-Mail or password incorrect.</span>
            </label>
            <label>Password
                <input type="password" v-model="password"/>
                <span v-if="attempted" class="error">E-Mail or password incorrect.</span>
            </label>
            <div>
                <button>Log in</button>
            </div>
        </form>
    </div>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';

import { BUSY } from '../store/index';

@Options({
})
export default class Login extends Vue {
    public email = '';
    public password = '';
    public attempted = false;

    public get isAuthenticating() {
        return this.$store.state.user.state === BUSY;
    }

    public login() {
        this.$store.dispatch('authenticateEmailPassword', {
            email: this.email,
            password: this.password,
        });
        this.attempted = true;
    }
}
</script>
