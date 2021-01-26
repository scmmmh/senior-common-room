<template>
    <div v-if="isAuthenticating" role="alert" aria-modal="true">
        <div>
            <h2 id="authenticating-title">Senior Common Room - Authenticating</h2>
            <p>The authentication is in progress... Please wait...</p>
        </div>
    </div>
    <div v-else role="dialog" aria-modal="true" aria-labelledby="login-title">
        <div>
            <h2 id="login-title">Senior Common Room - Login</h2>
            <form @submit="login">
                <label :class="{'error': attempted}">E-Mail
                    <input type="email" v-model="email"/>
                    <span v-if="attempted" class="error">E-Mail or password incorrect.</span>
                </label>
                <label :class="{'error': attempted}">Password
                    <input type="password" v-model="password"/>
                    <span v-if="attempted" class="error">E-Mail or password incorrect.</span>
                </label>
                <div>
                    <button class="button primary">Log in</button>
                </div>
            </form>
        </div>
    </div>
</template>

<script lang="ts">
import { Options } from 'vue-class-component';

import { ComponentRoot } from '../base';
import { localLoadValue } from '../util/storage';
import { BUSY } from '../store/index';

@Options({
})
export default class Login extends ComponentRoot {
    public email = localLoadValue('user.email', '');
    public password = '';
    public attempted = false;

    public get isAuthenticating() {
        return this.$store.state.user.state === BUSY;
    }

    public login(ev: Event) {
        ev.preventDefault();
        this.$store.dispatch('authenticateEmailPassword', {
            email: this.email,
            password: this.password,
        });
        this.attempted = true;
    }
}
</script>
