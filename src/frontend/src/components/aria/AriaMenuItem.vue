<template>
    <li role="presentation">
        <a role="menuitem" @click="click" @keyup="keyUp" :tabindex="tabindex" :aria-current="current ? 'page': null"><slot></slot></a>
    </li>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';

@Options({
    props: {
        href: String,
        tabindex: {
            type: String,
            default: '-1',
        },
        current: {
            type: Boolean,
            default: false,
        },
    },
    emits: {
        click: null,
    },
})
export default class AriaMenuItem extends Vue {
    href!: string;
    tabindex!: number;
    current!: boolean;

    public click(ev: MouseEvent): void {
        ev.preventDefault();
        this.$emit('click');
    }

    public keyUp(ev: KeyboardEvent): void {
        if (ev.keyCode === 13) {
            const elem = this.$el;
            if (elem.children.length === 2) {
                // Handle child menu
            } else {
                this.$emit('click');
            }
        } else if (ev.keyCode === 27) {
            console.log('escape');
        } else if (ev.keyCode === 37) {
            const elem = this.$el;
            if (elem.parentElement.getAttribute('role') === 'menubar' && elem.previousElementSibling) {
                const prevItem = elem.previousElementSibling.querySelector(':scope > [role="menuitem"]');
                if (prevItem) {
                    prevItem.focus();
                }
            }
        } else if (ev.keyCode === 39) {
            const elem = this.$el;
            if (elem.parentElement.getAttribute('role') === 'menubar' && elem.nextElementSibling) {
                const nextItem = elem.nextElementSibling.querySelector(':scope > [role="menuitem"]');
                if (nextItem) {
                    nextItem.focus();
                }
            }
        }
    }
}
</script>
