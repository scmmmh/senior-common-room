<script lang="ts">
	import { fade } from 'svelte/transition';

    import { overlay } from '../store';
    import IFrameOverlay from './IFrameOverlay.svelte';
    import JitsiOverlay from './JitsiOverlay.svelte';

    function hideOverlay() {
        overlay.set(null);
    }
</script>

{#if $overlay}
    <div transition:fade="{{ duration: 100 }}" on:click={hideOverlay} class="fixed top-0 left-0 w-screen h-screen bg-black bg-opacity-60 z-10">
        {#if $overlay.type === 'iframe'}
            <IFrameOverlay/>
        {:else if $overlay.type === 'jitsi-room'}
            <JitsiOverlay/>
        {/if}
    </div>
{/if}
