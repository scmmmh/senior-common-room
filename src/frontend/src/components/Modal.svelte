<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { fade } from 'svelte/transition';

	const dispatch = createEventDispatcher();

    let modalElement = null as HTMLElement;

    function close() {
        dispatch('close');
    }

    function modalClose(ev: MouseEvent) {
        if (ev.target === modalElement) {
            close();
            ev.preventDefault();
        }
    }
</script>

<div bind:this={modalElement} transition:fade="{{ duration: 100 }}" on:click={modalClose} class="fixed top-0 left-0 w-screen h-screen bg-black bg-opacity-60 z-10">
    <slot close={close}></slot>
</div>
