<script lang="ts">
    import { onDestroy, tick } from 'svelte';

    import { overlay } from '../store';
    import CloseOverlay from './CloseOverlay.svelte';

    let iframe = null;

    const unsubscribe = overlay.subscribe((overlay) => {
        if (overlay && overlay.type === 'iframe') {
            tick().then(() => {
                if (iframe) {
                    iframe.focus();
                }
            })
        }
    });

    onDestroy(unsubscribe);
</script>

{#if $overlay}
    <div class="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 h-5/6 w-11/12 max-w-5xl bg-white border-3 border-yellow-300 rounded">
        <CloseOverlay/>
        <iframe bind:this={iframe} title="" class="w-full h-full" src={$overlay.url}/>
    </div>
{/if}
