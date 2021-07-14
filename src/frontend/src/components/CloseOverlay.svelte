<script lang="ts">
    import { onDestroy, tick } from 'svelte';

    import { overlay } from '../store';

    function hideOverlay() {
        overlay.set(null);
    }
</script>

<button on:click={hideOverlay} aria-label="Close" class="block absolute right-0 top-0 rounded bg-gray-700 text-white px-2 py-2 shadow-2xl z-50">
    <svg class="w-4 h-4" viewBox="0 0 24 24">
        <path fill="currentColor" d="M20 6.91L17.09 4L12 9.09L6.91 4L4 6.91L9.09 12L4 17.09L6.91 20L12 14.91L17.09 20L20 17.09L14.91 12L20 6.91Z" />
    </svg>
</button>
