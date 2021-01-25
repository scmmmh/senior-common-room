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
    watch: {
        rid(newValue, oldValue) {
            if (oldValue) {
                this.$store.dispatch('leaveRoom', oldValue);
            }
            if (newValue) {
                this.$store.dispatch('enterRoom', newValue);
            }
        }
    }
})
export default class RoomView extends ComponentRoot {
    public get rid() {
        if (this.$route.name === 'room') {
            return this.$route.params.rid;
        } else {
            return null;
        }
    }

    public mounted() {
        this.$store.dispatch('enterRoom', this.$route.params.rid);
    }

}
</script>
