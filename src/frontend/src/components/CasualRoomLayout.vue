<template>
    <div class="chat">
        <h2 class="show-for-sr">Chat messages</h2>
        <ol>
            <li>
                <h3>Somebody</h3>
                <p>Just some text</p>
            </li>
            <li>
                <h3>Somebody Else</h3>
                <p>Just some text</p>
            </li>
            <li>
                <h3>Another</h3>
                <p>Just some text</p>
            </li>
        </ol>
    </div>
    <div class="people">
        <h2 class="show-for-sr">People in the room</h2>
        <ol>
            <li>
                <h3>Some Administrator</h3>
            </li>
            <li>
                <h3>Some Presenter</h3>
            </li>
            <li>
                <h3>Another Presenter</h3>
            </li>
            <li>
                <h3>A Participant</h3>
            </li>
            <li>
                <h3>Another Participant</h3>
            </li>
            <li>
                <h3>The Participant</h3>
            </li>
            <li>
                <h3>Some Participant</h3>
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
}
</script>
