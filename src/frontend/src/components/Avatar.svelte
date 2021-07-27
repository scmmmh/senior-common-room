<script lang="ts">
    import { slide } from 'svelte/transition';

    export let avatar: UpdateAvatarLocationPayload;
    export let x: number;
    export let y: number;
    let distance = 0;

    function updateDistance() {
        distance = Math.sqrt(Math.pow(Math.abs(x - avatar.x), 2) + Math.pow(Math.abs(y - avatar.y), 2));
        console.log(distance);
    }

    updateDistance();

    $: {
        updateDistance();
    }
</script>

<li in:slide out:slide class="flex">
    <div class="flex-0"><img src="{avatar.user.avatar}-small.png" alt=""/></div>
    <div class="flex-1 flex flex-col pl-4">
        <p class="font-bold tracking-widest mb-2 border-yellow-400 border-b-1">{avatar.user.name}</p>
        <nav>
            <ul class="flex">
                <li class="flex-0">
                    <button class="block" aria-label="Send a message">
                        <svg viewBox="0 0 24 24" class="w-6 h-6">
                            <path fill="currentColor" d="M20,2H4A2,2 0 0,0 2,4V22L6,18H20A2,2 0 0,0 22,16V4A2,2 0 0,0 20,2M6,9H18V11H6M14,14H6V12H14M18,8H6V6H18" />
                        </svg>
                    </button>
                </li>
                {#if distance < 3}
                    <li class="flex-0">
                        <button class="block" aria-label="Start a video chat">
                            <svg viewBox="0 0 24 24" class="w-6 h-6">
                                <path fill="currentColor" d="M18,14L14,10.8V14H6V6H14V9.2L18,6M20,2H4A2,2 0 0,0 2,4V22L6,18H20A2,2 0 0,0 22,16V4C22,2.89 21.1,2 20,2Z" />
                            </svg>
                        </button>
                    </li>
                {/if}
            </ul>
        </nav>
    </div>
</li>
