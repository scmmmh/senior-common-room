<script lang="ts">
    import { isConnecting, isReconnecting, isFailed, isDisconnected, connect, reconnectWait } from '../store';

    import Dialog from './Dialog.svelte';
    import Button from './Button.svelte';
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
                The connection to the Senior Common Room has failed. <Button on:click={connect}>Click here to attempt to reconnect.</Button>
            {:else if $isDisconnected}
                The connection to the Senior Common Room has been lost. You will be reconnected automatically in {$reconnectWait} second{#if $reconnectWait > 1}s{/if}.
            {/if}
        </div>
    </Dialog>
</div>
