<script lang="ts">
	import { createEventDispatcher } from 'svelte';

    export let type = 'primary';
    let cls = '';
    export { cls as class };
    export let title = '';
    let typeCls = '';

    $: {
    if (type === 'primary') {
        typeCls = 'px-3 py-2 font-medium bg-yellow-400 text-black';
    } else if (type === 'secondary') {
        typeCls = 'px-3 py-2 bg-gray-300 text-black';
    } else if (type === 'primary-outline') {
        typeCls = 'px-3 py-2 border-2 border-yellow-400';
    } else if (type === 'icon') {
        typeCls = 'p-2 transition-colors hover:bg-yellow-400 hover:text-black rounded';
    } else if (type === 'icon-selected') {
        typeCls = 'p-2 transition-colors bg-yellow-400 text-black rounded';
    }
    }

    const dispatch = createEventDispatcher();
</script>

<button on:click={(ev) => { dispatch('click', ev); }} class="inline-block {typeCls} {cls}" title={title} aria-label={$$props['aria-label']}><slot></slot></button>
