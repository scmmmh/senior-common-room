<script lang="ts">
    import { isConnecting, isReconnecting, isFailed, isDisconnected } from '../store';

    import Dialog from './Dialog.svelte';
</script>

<div class="w-screen h-screen bg-gray-700">
    <Dialog class="bg-white">
        <span slot="title">
            {#if $isConnecting}
                Connecting... Please wait...
            {:else if $isReconnecting}
                Connecting... Please wait...
            {:else if $isFailed}
                Connection failed
            {:else if $isDisconnected}
                Connection lost
            {/if}
        </span>
        <div slot="content">
            {#if $isConnecting}
                You are being connected to the Senior Common Room. Please wait...
            {:else if $isReconnecting}
                You are being reconnected to the Senior Common Room. Please wait...
            {:else if $isFailed}
                The connection to the Senior Common Room has failed.
            {:else if $isDisconnected}
                The connection to the Senior Common Room has been lost. You will be reconnected automatically.
            {/if}
        </div>
    </Dialog>
</div>
