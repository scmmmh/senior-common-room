<script lang="ts">
    import { Link, useLocation } from "svelte-navigator";

    import { rooms, executeAction, user, schedule, showSchedule } from '../store';

    const location = useLocation();

    function logout() {
        executeAction.set({
            action: 'logout'
        });
    }

    function showScheduleClick(ev: Event) {
        ev.preventDefault();
        showSchedule.set(true);
    }
</script>

<nav class="flex-0 bg-gray-700 text-white font-xl">
    <ul class="flex">
        {#each $rooms as room}
            <li role="presentation" class="flex-0"><Link to="/room/{room.slug}" class="block px-4 py-3 tracking-wider border-b-4 {$location.pathname.startsWith('/room/' + room.slug) ? 'border-yellow-300' : 'border-gray-700'} hover:border-yellow-300">{room.label}</Link></li>
        {/each}
        <li role="presentation" class="flex-1"></li>
        {#if $schedule.length > 0}
            <li role="presentation" class="flex-0"><button on:click={showScheduleClick} class="block px-4 py-3 tracking-wider border-b-4 border-gray-700 hover:border-yellow-300">Schedule</button></li>
        {/if}
        <li role="presentation" class="flex-0">
            <Link to="/profile" class="flex flex-col place-content-center px-4 border-b-4 border-gray-700 {$location.pathname === '/profile' ? 'border-yellow-300' : 'border-gray-700'} hover:border-yellow-300 h-full">
                <img src={$user.avatar + '-small.png'} alt={$user.name} class="h-6"/>
            </Link>
        </li>
        <li role="presentation" class="flex-0"><button on:click={logout} class="block px-4 py-3 tracking-wider border-b-4 border-gray-700 hover:border-yellow-300">Logout</button></li>
    </ul>
</nav>
