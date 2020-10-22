<template>
    <div role="tabpanel" :id="id + '-tabpanel'" :tabindex="selected ? 0 : -1" :hidden="selected ? null : 'hidden'" :aria-labelledby="id + '-tab'">
        <slot></slot>
    </div>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';

@Options({
    props: {
        id: String,
        selected: {
            type: Boolean,
            default: false,
        },
    },
})
export default class AriaTabPanel extends Vue {
    id!: string;
    selected!: boolean;
}
</script>
