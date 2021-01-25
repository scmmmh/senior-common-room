<template>
    <div class="lobby">
        <h1>Welcome to the Senior Common Room</h1>
        <p>Please step through these doors.</p>
    </div>
</template>

<script lang="ts">
import { Options } from 'vue-class-component';

import { ComponentRoot } from '../base';
import { RoomState } from '@/store';

@Options({
    components: {
    },
    watch: {
        lobbyId(newValue: string) {
            if (newValue !== '') {
                this.$router.push({name: 'room', params: {rid: newValue}});
            }
        }
    }
})
export default class Lobby extends ComponentRoot {
    public get lobbyId() {
        return Object.values(this.$store.state.rooms).reduce((acc: string, room: RoomState) => {
            if (room.lobby) {
                return room.id;
            } else {
                return  acc;
            }
        }, '');
    }

    public mounted() {
        if (this.lobbyId) {
            this.$router.push({name: 'room', params: {rid: this.lobbyId}});
        }
    }
}
</script>
