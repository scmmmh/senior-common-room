<template>
    <div class="lobby">
        <room :questions="false"/>
    </div>
</template>

<script lang="ts">
import { Options } from 'vue-class-component';

import { ComponentRoot } from '../base';
import Room from '../components/Room.vue';

@Options({
    components: {
        Room,
    },
})
export default class Lobby extends ComponentRoot {
    public mounted() {
        this.$store.dispatch('enterRoom', 'lobby');
    }

    public unmounted() {
        this.$store.dispatch('leaveRoom', 'lobby');
    }
}
</script>
