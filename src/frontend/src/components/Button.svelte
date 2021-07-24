<script lang="ts">
	import { createEventDispatcher } from 'svelte';

    export let type = 'primary';
    let cls = '';
    export { cls as class };
    let typeCls = '';

    if (type === 'primary') {
        typeCls = 'font-medium bg-yellow-400 text-black';
    } else if (type === 'secondary') {
        typeCls = 'bg-gray-300';
    } else if (type === 'primary-outline') {
        typeCls = 'border-2 border-yellow-400'
    }

    const dispatch = createEventDispatcher();
</script>

<button on:click={(ev) => { dispatch('click', ev); }} class="inline-block px-3 py-2 {typeCls} {cls}"><slot></slot></button>
