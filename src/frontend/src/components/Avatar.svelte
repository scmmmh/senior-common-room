<script lang="ts">
    import { slide } from 'svelte/transition';

    import SendMessage from './SendMessage.svelte';
    import Button from './Button.svelte';

    export let avatar: UpdateAvatarLocationPayload;
    export let x: number;
    export let y: number;
    let distance = Math.sqrt(Math.pow(Math.abs(x - avatar.x), 2) + Math.pow(Math.abs(y - avatar.y), 2));
    let showUserMessage = false;

    $: {
        distance = Math.sqrt(Math.pow(Math.abs(x - avatar.x), 2) + Math.pow(Math.abs(y - avatar.y), 2));
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
            <SendMessage on:close={() => { showUserMessage = false; }} type="user-message" user={avatar.user}>Send message to {avatar.user.name}</SendMessage>
        {/if}
    </div>
</li>
