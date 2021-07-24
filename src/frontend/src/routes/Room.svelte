<script lang="ts">
    import { derived } from 'svelte/store';

    import Map from '../components/Map.svelte';
    import { rooms, action, executeAction, actionLabel } from '../store';

    export let rid: string;

    const roomConfig = derived(rooms, (rooms) => {
        for (let idx = 0; idx < rooms.length; idx++) {
            if (rooms[idx].slug === rid) {
                return rooms[idx];
            }
        }
        return null;
    });

    function runAction() {
        executeAction.set($action);
    }
</script>

<div class="v-full h-full overflow-hidden flex">
    {#if $roomConfig}
        <h1 class="sr-only">{$roomConfig.label}</h1>
        <Map/>
        {#if $action}
            <button on:click={runAction} class="block fixed bottom-4 left-1/2 z-10 bg-gray-700 border-3 border-yellow-300 rounded-lg shadow-lg px-4 py-2 transform -translate-x-1/2 text-white uppercase tracking-widest">{$actionLabel}</button>
        {/if}
    {:else}
        <h1>Loading...</h1>
    {/if}
</div>
