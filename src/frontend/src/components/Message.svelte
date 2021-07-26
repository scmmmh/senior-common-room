<script lang="ts">
    import { onMount, onDestroy, createEventDispatcher } from 'svelte';
    import { slide } from 'svelte/transition';

	const dispatch = createEventDispatcher();

    export let countdown = 30;
    const circumference = 28 * Math.PI;
    let circle;
    let current = 0;
    let countdownInterval = -1;

    function close() {
        window.clearInterval(countdownInterval);
        dispatch('close');
    }

    function startCountdown() {
        countdownInterval = window.setInterval(() => {
            current = current + 1
            circle.style.strokeDashoffset = circumference * current / countdown;
            if (current >= countdown) {
                window.clearInterval(countdownInterval);
                close();
            }
        }, 1000);
    }

    function clearCountdown() {
        window.clearInterval(countdownInterval);
        circle.style.strokeDashoffset = 0;
        current = 0;
    }

    onMount(() => {
        circle.style.transition = 'stroke-dashoffset 0.95s';
        circle.style.transform = 'rotate(-90deg)';
        circle.style.transformOrigin = '50% 50%';
        circle.style.strokeDasharray = circumference + ' ' + circumference;
        circle.style.strokeDashoffset = 0;

        startCountdown();
    });

    onDestroy(() => {
        window.clearInterval(countdownInterval);
    });
</script>

<li on:mouseenter={clearCountdown} on:mouseleave={startCountdown} in:slide out:slide class="bg-gray-700 text-white rounded-lg mb-6 px-4 py-3 relative border-2 border-yellow-400">
    <button on:click={close} aria-label="Dismiss this message" class="absolute -top-3 -right-3 rounded-full bg-gray-700">
        <svg viewBox="0 0 24 24" class="w-6 h-6 p-1">
            <path fill="currentColor" d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z" />
        </svg>
        <svg viewBox="0 0 24 24" class="absolute top-0 left-0 w-full h-full text-yellow-400">
            <circle bind:this={circle} stroke="currentColor" stroke-width="2" fill="transparent" r="10" cx="12" cy="12"/>
        </svg>
    </button>
    <slot></slot>
</li>
