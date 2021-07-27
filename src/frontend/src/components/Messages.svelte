<script lang="ts">
    import { onDestroy } from 'svelte';

    import { messages, user } from '../store';
    import Message from './Message.svelte';
    import Button from './Button.svelte';
    import SendMessage from './SendMessage.svelte';

    let currentMessages = [];
    let nextMessageId = 1;
    let showUserMessage = false;

    const unsubscribeMessages = messages.subscribe((message) => {
        if (message.type === 'broadcast-message') {
            currentMessages.push({
                id: nextMessageId,
                payload: {
                    type: 'broadcast',
                    message: (message.payload as BroadcastMessagePayload).message,
                }
            });
            currentMessages = currentMessages;
            nextMessageId = nextMessageId + 1;
        } else if (message.type === 'user-message') {
            currentMessages.push({
                id: nextMessageId,
                payload: {
                    type: 'user',
                    user: (message.payload as UserMessagePayload).user,
                    message: (message.payload as UserMessagePayload).message
                }
            });
            currentMessages = currentMessages;
            nextMessageId = nextMessageId + 1;
        }
    });

    function closeMessage(id: string) {
        currentMessages = currentMessages.filter((msg) => { return msg.id !== id; });
    }

    function format(str: string): string {
        str = str.trim();
        str = str.replaceAll('\n', '</p><p>');
        return '<p>' + str + '</p>';
    }

    onDestroy(unsubscribeMessages);
</script>

<div class="fixed right-0 bottom-0 px-7 w-full md:w-1/3 lg:w-1/4 z-50">
    <ol>
        {#each currentMessages as msg (msg.id)}
            <Message on:close={() => { closeMessage(msg.id); }} countdown={msg.payload.type === 'broadcast' ? 30 : 15}>
                {#if msg.payload.type === 'broadcast'}
                    <div>
                        <div class="border-yellow-400 border-b-1 pb-2 mb-2">
                            <svg viewBox="0 0 24 24" class="w-6 h-6">
                                <path fill="currentColor" d="M12 10C10.9 10 10 10.9 10 12S10.9 14 12 14 14 13.1 14 12 13.1 10 12 10M18 12C18 8.7 15.3 6 12 6S6 8.7 6 12C6 14.2 7.2 16.1 9 17.2L10 15.5C8.8 14.8 8 13.5 8 12.1C8 9.9 9.8 8.1 12 8.1S16 9.9 16 12.1C16 13.6 15.2 14.9 14 15.5L15 17.2C16.8 16.2 18 14.2 18 12M12 2C6.5 2 2 6.5 2 12C2 15.7 4 18.9 7 20.6L8 18.9C5.6 17.5 4 14.9 4 12C4 7.6 7.6 4 12 4S20 7.6 20 12C20 15 18.4 17.5 16 18.9L17 20.6C20 18.9 22 15.7 22 12C22 6.5 17.5 2 12 2Z" />
                            </svg>
                        </div>
                        {@html format(msg.payload.message)}
                    </div>
                {:else if msg.payload.type === 'user'}
                    <div>
                        <div class="border-yellow-400 border-b-1 pb-2 mb-2 flex items-center">
                            <img src="{msg.payload.user.avatar}-small.png" alt="" class="w-6 h-6 flex-0"/>
                            <span class="flex-1 tracking-wider px-2">{msg.payload.user.name}</span>
                            <Button on:click={() => { showUserMessage = true; }} type="icon">
                                <svg viewBox="0 0 24 24" class="w-6 h-6">
                                    <path fill="currentColor" d="M18,8H6V6H18V8M18,11H6V9H18V11M18,14H6V12H18V14M22,4A2,2 0 0,0 20,2H4A2,2 0 0,0 2,4V16A2,2 0 0,0 4,18H18L22,22V4Z" />
                                </svg>
                            </Button>
                        </div>
                        {@html format(msg.payload.message)}
                        {#if showUserMessage}
                            <SendMessage on:close={(ev) => { showUserMessage = false; if (ev.detail.sent) { closeMessage(msg.id); } }} type="user-message" user={msg.payload.user}>Send message to {msg.payload.user.name}</SendMessage>
                        {/if}
                    </div>
                {/if}
            </Message>
        {/each}
    </ol>
</div>
