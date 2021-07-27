<script lang="ts">
    import Avatar from './Avatar.svelte';
    import Button from './Button.svelte';

    export let avatars = [];
    export let x = 0;
    export let y = 0;
    let visible = false;
</script>

<div class="fixed left-0 top-0 h-screen pt-20 pb-4 z-40">
    <div class="bg-gray-700 text-white rounded-r-lg py-4 pl-2 pr-4 max-h-full flex flex-col">
        <h2 class="sr-only">People in the room</h2>
        <div class="flex-0 text-right {visible ? 'mb-4' : ''}">
            <Button type={visible ? 'icon-selected' : 'icon'} on:click={() => { visible = !visible; }} aria-label={visible ? 'Hide administration functions' : 'Show administration functions'}>
                <svg viewBox="0 0 24 24" class="w-6 h-6">
                    <path fill="currentColor" d="M16 17V19H2V17S2 13 9 13 16 17 16 17M12.5 7.5A3.5 3.5 0 1 0 9 11A3.5 3.5 0 0 0 12.5 7.5M15.94 13A5.32 5.32 0 0 1 18 17V19H22V17S22 13.37 15.94 13M15 4A3.39 3.39 0 0 0 13.07 4.59A5 5 0 0 1 13.07 10.41A3.39 3.39 0 0 0 15 11A3.5 3.5 0 0 0 15 4Z" />
                </svg>
            </Button>
        </div>
        {#if visible}
            <ul class="flex-1 overflow-auto w-full md:w-60">
                {#each avatars as avatar (avatar.user.id)}
                    <Avatar avatar={avatar} x={x} y={y}/>
                {:else}
                    <li>You are currently on your own here</li>
                {/each}
            </ul>
        {/if}
    </div>
</div>
