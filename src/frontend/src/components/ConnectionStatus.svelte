<script lang="ts">
    import { isConnecting, isReconnecting, isFailed, isDisconnected, connect, reconnectWait, coreConfig } from '../store';

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
                You are being connected to {$coreConfig.title}. Please wait...
            {:else if $isReconnecting}
                You are being reconnected to the {$coreConfig.title}. Please wait...
            {:else if $isFailed}
                The connection to the {$coreConfig.title} has failed. <Button on:click={connect}>Click here to attempt to reconnect.</Button>
            {:else if $isDisconnected}
                The connection to the {$coreConfig.title} has been lost. The system will try to automatically reconnect in {$reconnectWait} second{#if $reconnectWait > 1}s{/if}.
            {/if}
        </div>
    </Dialog>
</div>
