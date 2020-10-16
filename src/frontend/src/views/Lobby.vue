<template>
    <div class="lobby">
        Lobby
    </div>
</template>

<script lang="ts">
import { Options } from 'vue-class-component';

import { ComponentRoot } from '../base';

@Options({
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
