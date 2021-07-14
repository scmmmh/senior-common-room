<script lang="ts">
	import { createEventDispatcher } from 'svelte';

    export let type = 'primary';
    let cls = '';
    export { cls as class };

    const dispatch = createEventDispatcher();
</script>

<button on:click={(ev) => { dispatch('click', ev); }} class="inline-block px-3 py-2 {type === 'primary' ? 'font-medium bg-yellow-400' : 'bg-gray-300'} {cls}"><slot></slot></button>
