<script lang="ts">
    import { onDestroy } from 'svelte';

    import { messages } from '../store';
    import Message from './Message.svelte';

    const unsubscribeMessages = messages.subscribe((message) => {
    });

    onDestroy(unsubscribeMessages);
</script>

<div class="fixed right-0 bottom-0 mr-7">
    <ol>
        <Message>Testing</Message>
        <Message>Testing</Message>
    </ol>
</div>
