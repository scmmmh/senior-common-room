<script lang="ts">
    import { slide } from 'svelte/transition';
    import { derived } from 'svelte/store';

    import { sendMessage, user, jitsiRoomUsers, overlay } from '../store';
    import SendMessage from './SendMessage.svelte';
    import Button from './Button.svelte';

    export let avatar: UpdateAvatarLocationPayload;
    export let x: number;
    export let y: number;
    let distance = Math.sqrt(Math.pow(Math.abs(x - avatar.x), 2) + Math.pow(Math.abs(y - avatar.y), 2));
    let showUserMessage = false;
    let videoInviteSentTimeout = null;

    $: {
        distance = Math.sqrt(Math.pow(Math.abs(x - avatar.x), 2) + Math.pow(Math.abs(y - avatar.y), 2));
    }

    const jitsiRoom = derived(overlay, (overlay) => {
        if (overlay && overlay.type === 'jitsi-room') {
            console.log(overlay);
            return {
                name: overlay.name,
            };
        } else {
            return null;
        }
    }, null);

    function requestVideoChat(ev: Event) {
        ev.preventDefault();
        clearTimeout(videoInviteSentTimeout);
        if ($jitsiRoom) {
            sendMessage({
                type: 'request-join-video-chat-message',
                payload: {
                    user: {
                        id: avatar.user.id
                    },
                    room: $jitsiRoom.name,
                }
            });
        } else {
            sendMessage({
                type: 'request-video-chat-message',
                payload: {
                    user: {
                        id: avatar.user.id
                    }
                }
            });
        }
        videoInviteSentTimeout = window.setTimeout(() => {
            videoInviteSentTimeout = null;
        }, 5000);
    }

    function toggleUserBlock(ev: Event) {
        ev.preventDefault();
        if ($user.blocked_users && $user.blocked_users.indexOf(avatar.user.id) >= 0) {
            sendMessage({
                type: 'unblock-user',
                payload: {
                    user: {
                        id: avatar.user.id
                    }
                }
            });
        } else {
            sendMessage({
                type: 'block-user',
                payload: {
                    user: {
                        id: avatar.user.id
                    }
                }
            });
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
                {#if distance < 3 && $jitsiRoomUsers.indexOf(avatar.user.id) < 0}
                    <li class="flex-0">
                        {#if videoInviteSentTimeout !== null}
                            <Button type="icon" class="block" aria-label="Invite sent" title="Invite sent">
                                <svg viewBox="0 0 24 24" class="w-6 h-6">
                                    <path fill="currentColor" d="M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z" />
                                </svg>
                            </Button>
                        {:else}
                            <Button type="icon" class="block" aria-label={$jitsiRoom ? 'Invite to join the video chat' : 'Start a video chat'} title={$jitsiRoom ? 'Invite to join the video chat' : 'Start a video chat'} on:click={requestVideoChat}>
                                <svg viewBox="0 0 24 24" class="w-6 h-6">
                                    <path fill="currentColor" d="M18,14L14,10.8V14H6V6H14V9.2L18,6M20,2H4A2,2 0 0,0 2,4V22L6,18H20A2,2 0 0,0 22,16V4C22,2.89 21.1,2 20,2Z" />
                                </svg>
                            </Button>
                        {/if}
                    </li>
                {/if}
                <li>
                    <Button type={$user.blocked_users && $user.blocked_users.indexOf(avatar.user.id) >= 0 ? 'icon-selected' : 'icon'} class="block" aria-label="Block this user" title="Block this user" on:click={toggleUserBlock}>
                        <svg viewBox="0 0 24 24" class="w-6 h-6">
                            <path fill="currentColor" d="M10 4A4 4 0 0 0 6 8A4 4 0 0 0 10 12A4 4 0 0 0 14 8A4 4 0 0 0 10 4M17.5 13C15 13 13 15 13 17.5C13 20 15 22 17.5 22C20 22 22 20 22 17.5C22 15 20 13 17.5 13M10 14C5.58 14 2 15.79 2 18V20H11.5A6.5 6.5 0 0 1 11 17.5A6.5 6.5 0 0 1 11.95 14.14C11.32 14.06 10.68 14 10 14M17.5 14.5C19.16 14.5 20.5 15.84 20.5 17.5C20.5 18.06 20.35 18.58 20.08 19L16 14.92C16.42 14.65 16.94 14.5 17.5 14.5M14.92 16L19 20.08C18.58 20.35 18.06 20.5 17.5 20.5C15.84 20.5 14.5 19.16 14.5 17.5C14.5 16.94 14.65 16.42 14.92 16Z" />
                        </svg>
                    </Button>
                </li>
            </ul>
        </nav>
        {#if showUserMessage}
            <SendMessage on:close={() => { showUserMessage = false; }} type="user-message" user={avatar.user}>Send message to {avatar.user.name}</SendMessage>
        {/if}
    </div>
</li>
