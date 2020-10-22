<template>
    <div class="room">
        <div class="sidebar">
            <nav>
                <ul role="tablist">
                    <aria-tab :selected="sidebarTab === 'people'" id="people" @click="setSidebarTab('people')">People</aria-tab>
                    <aria-tab :selected="sidebarTab === 'chat'" id="chat" @click="setSidebarTab('chat')">Chat</aria-tab>
                    <aria-tab v-if="questions" :selected="sidebarTab === 'questions'" id="questions" @click="setSidebarTab('questions')">Questions</aria-tab>
                </ul>
            </nav>
            <aria-tab-panel :selected="sidebarTab === 'people'" id="people">
                People
            </aria-tab-panel>
            <aria-tab-panel :selected="sidebarTab === 'chat'" id="chat">
                Chat
            </aria-tab-panel>
            <aria-tab-panel v-if="questions" :selected="sidebarTab === 'questions'" id="questions">
                Questions
            </aria-tab-panel>
        </div>
    </div>
</template>

<script lang="ts">
import { Options } from 'vue-class-component';

import { ComponentRoot } from '../base';
import AriaTab from './aria/AriaTab.vue';
import AriaTabPanel from './aria/AriaTabPanel.vue';

@Options({
    components: {
        AriaTab,
        AriaTabPanel,
    },
    props: {
        questions: {
            type: Boolean,
            default: true,
        }
    }
})
export default class Room extends ComponentRoot {
    public sidebarTab = 'people';

    public setSidebarTab(newSidebarTab: string) {
        this.sidebarTab = newSidebarTab;
    }
}
</script>
