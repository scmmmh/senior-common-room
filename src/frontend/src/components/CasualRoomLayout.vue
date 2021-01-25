<template>
    <div class="chat">
        <h2 class="show-for-sr">Chat messages</h2>
        <ol>
            <li v-for="(message, idx) in messages" :key="idx">
                <h3>{{ message.user.id === $store.state.user.id ? 'You' : message.user.name }}</h3>
                <p>{{ message.message }}</p>
            </li>
        </ol>
    </div>
    <div class="people">
        <h2 class="show-for-sr">People in the room</h2>
        <ol>
            <li>
                <h3>{{ $store.state.user.name }}</h3>
            </li>
            <li v-for="user in users" :key="user.id">
                <h3>{{ user.name }}</h3>
            </li>
        </ol>
    </div>
</template>

<script lang="ts">
import { Options } from 'vue-class-component';

import { ComponentRoot } from '../base';

@Options({
})
export default class CasualRoomLayout extends ComponentRoot {
    public get users() {
        const users = Object.values(this.$store.state.users);
        users.sort((a, b) => {
            if (a.name < b.name) {
                return -1;
            } else if (a.name > b.name) {
                return 1;
            } else {
                return 0;
            }
        });
        return users;
    }

    public get messages() {
        return this.$store.state.messages;
    }
}
</script>
