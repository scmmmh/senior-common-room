<script lang="ts">
    import { slide } from 'svelte/transition';

    export let users = [];
    let visible = false;
</script>

<div class="fixed left-0 top-0 h-screen pt-20 pb-4 z-50">
    <div class="bg-gray-700 text-white rounded-r-lg py-4 pl-2 pr-4 max-h-full flex flex-col">
        <h2 class="sr-only">People in the room</h2>
        <div class="flex-0 text-right {visible ? 'mb-4' : ''}">
            <button on:click={() => { visible = !visible; }} aria-label={visible ? 'Hide administration functions' : 'Show administration functions'}>
                <svg viewBox="0 0 24 24" class="w-8 h-8">
                    <path fill="currentColor" d="M16 17V19H2V17S2 13 9 13 16 17 16 17M12.5 7.5A3.5 3.5 0 1 0 9 11A3.5 3.5 0 0 0 12.5 7.5M15.94 13A5.32 5.32 0 0 1 18 17V19H22V17S22 13.37 15.94 13M15 4A3.39 3.39 0 0 0 13.07 4.59A5 5 0 0 1 13.07 10.41A3.39 3.39 0 0 0 15 11A3.5 3.5 0 0 0 15 4Z" />
                </svg>
            </button>
        </div>
        {#if visible}
            <ul class="flex-1 overflow-auto w-full md:w-60">
                {#each users as user (user.id)}
                    <li in:slide out:slide class="flex">
                        <div class="flex-0"><img src="{user.avatar}-small.png" alt=""/></div>
                        <div class="flex-1 flex flex-col pl-4">
                            <p class="font-bold tracking-widest mb-2 border-yellow-400 border-b-1">{user.name}</p>
                            <nav>
                                <ul class="flex">
                                    <li class="flex-0">
                                        <button class="block">
                                            <svg viewBox="0 0 24 24" class="w-6 h-6">
                                                <path fill="currentColor" d="M20,2H4A2,2 0 0,0 2,4V22L6,18H20A2,2 0 0,0 22,16V4A2,2 0 0,0 20,2M6,9H18V11H6M14,14H6V12H14M18,8H6V6H18" />
                                            </svg>
                                        </button>
                                    </li>
                                </ul>
                            </nav>
                        </div>
                    </li>
                {:else}
                    <li>You are currently on your own here</li>
                {/each}
            </ul>
        {/if}
    </div>
</div>
