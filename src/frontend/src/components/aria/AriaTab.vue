<template>
    <li role="presentation">
        <a role="tab" @click="click" @keyup="keyUp" :id="id + '-tab'" :aria-controls="id + '-tabpanel'" :tabindex="selected ? '0' : '-1'" :aria-selected="selected ? 'true': 'false'"><slot></slot></a>
    </li>
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
    emits: {
        click: null,
    },
})
export default class AriaTab extends Vue {
    id!: string;
    selected!: boolean;

    public click(ev: MouseEvent): void {
        ev.preventDefault();
        this.$emit('click');
    }

    public keyUp(ev: KeyboardEvent): void {
        if (ev.keyCode === 13 || ev.keyCode === 32) {
            this.$emit('click');
        } else if (ev.keyCode === 37) {  // previous tab
            const elem = this.$el;
            if (elem.previousElementSibling) {
                const prevItem = elem.previousElementSibling.querySelector(':scope > [role="tab"]');
                if (prevItem) {
                    prevItem.focus();
                }
            }
        } else if (ev.keyCode === 39) {  // next tab
            const elem = this.$el;
            if (elem.nextElementSibling) {
                const nextItem = elem.nextElementSibling.querySelector(':scope > [role="tab"]');
                if (nextItem) {
                    nextItem.focus();
                }
            }
        } else if (ev.keyCode === 36) {  // first tab
            const elem = this.$el;
            if (elem.parentElement) {
                const firstItem = elem.parentElement.querySelector(':scope > li:first-child > [role="tab"]');
                if (firstItem) {
                    firstItem.focus();
                }
            }
        } else if (ev.keyCode === 35) {  // last tab
            const elem = this.$el;
            if (elem.parentElement) {
                const lastItem = elem.parentElement.querySelector(':scope > li:last-child > [role="tab"]');
                if (lastItem) {
                    lastItem.focus();
                }
            }
        }
    }
}
</script>
