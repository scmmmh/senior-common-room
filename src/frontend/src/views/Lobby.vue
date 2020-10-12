<template>
    <div class="lobby">
        Lobby
    </div>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';

@Options({
})
export default class Lobby extends Vue {
    public mounted() {
        this.$store.dispatch('enterRoom', 'lobby');
    }

    public unmounted() {
        this.$store.dispatch('leaveRoom', 'lobby');
    }
}
</script>
