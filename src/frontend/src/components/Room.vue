<template>
    <div id="room" :class="layout + '-layout'">
        <casual-room-layout v-if="layout === 'casual'"></casual-room-layout>
    </div>
</template>

<script lang="ts">
import { Options } from 'vue-class-component';

import { ComponentRoot } from '../base';
import CasualRoomLayout from './CasualRoomLayout.vue';

@Options({
    components: {
        CasualRoomLayout,
    }
})
export default class Room extends ComponentRoot {
    public layout = 'casual';
}
</script>
