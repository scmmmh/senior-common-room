<script lang="ts">
    import { slide } from 'svelte/transition';

    import { sendMessage } from '../store';
    import Modal from './Modal.svelte';
    import Dialog from './Dialog.svelte';
    import Button from './Button.svelte';
    import InputField from './InputField.svelte';

    export let avatar: UpdateAvatarLocationPayload;
    export let x: number;
    export let y: number;
    let distance = Math.sqrt(Math.pow(Math.abs(x - avatar.x), 2) + Math.pow(Math.abs(y - avatar.y), 2));
    let showUserMessage = false;
    let userMessage = '';
    let userMessageError = '';

    $: {
        distance = Math.sqrt(Math.pow(Math.abs(x - avatar.x), 2) + Math.pow(Math.abs(y - avatar.y), 2));
    }

    function sendUserMessage(ev: Event) {
        ev.preventDefault();
        if (userMessage.trim() !== '') {
            sendMessage({
                type: 'user-message',
                payload: {
                    user: {
                        id: avatar.user.id,
                    },
                    message: userMessage.trim(),
                }
            });
            userMessageError = '';
            showUserMessage = false;
        } else {
            userMessageError = 'Please provide a message';
        }
    }
</script>

<li in:slide out:slide class="flex">
    <div class="flex-0"><img src="{avatar.user.avatar}-small.png" alt=""/></div>
    <div class="flex-1 flex flex-col pl-4">
        <p class="tracking-wider mb-2 border-yellow-400 border-b-1">{avatar.user.name}</p>
        <nav>
            <ul class="flex">
                <li class="flex-0">
                    <Button type="icon" class="block" aria-label="Send a message" title="Send a message" on:click={() => { showUserMessage = true; }}>
                        <svg viewBox="0 0 24 24" class="w-6 h-6">
                            <path fill="currentColor" d="M20,2H4A2,2 0 0,0 2,4V22L6,18H20A2,2 0 0,0 22,16V4A2,2 0 0,0 20,2M6,9H18V11H6M14,14H6V12H14M18,8H6V6H18" />
                        </svg>
                    </Button>
                </li>
                {#if distance < 3}
                    <li class="flex-0">
                        <Button type="icon" class="block" aria-label="Start a video chat" title="Start a video chat">
                            <svg viewBox="0 0 24 24" class="w-6 h-6">
                                <path fill="currentColor" d="M18,14L14,10.8V14H6V6H14V9.2L18,6M20,2H4A2,2 0 0,0 2,4V22L6,18H20A2,2 0 0,0 22,16V4C22,2.89 21.1,2 20,2Z" />
                            </svg>
                        </Button>
                    </li>
                {/if}
            </ul>
        </nav>
        {#if showUserMessage}
            <form on:submit={sendUserMessage}>
                <Modal let:close={modalClose} on:close={() => { showUserMessage = false; }}>
                    <Dialog>
                        <span slot="title">Send a message to {avatar.user.name}</span>
                        <div slot="content">
                            <InputField type="textarea" bind:value={userMessage} error={userMessageError}>
                                Message
                            </InputField>
                        </div>
                        <div slot="actions">
                            <Button on:click={(ev) => { ev.preventDefault(); modalClose(); }} type="secondary">Don't Send</Button>
                            <Button type="primary">Send</Button>
                        </div>
                    </Dialog>
                </Modal>
            </form>
        {/if}
    </div>
</li>
