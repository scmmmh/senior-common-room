<script lang="ts">
import { Router, Route } from "svelte-navigator";

import MainNav from './components/MainNav.svelte';
import ConnectionStatus from './components/ConnectionStatus.svelte';
import Authentication from './components/Authentication.svelte';
import Room from './routes/Room.svelte';
import Profile from './routes/Profile.svelte';
import Schedule from './components/Schedule.svelte';
import Overlay from './components/Overlay.svelte';
import Onboarding from './components/Onboarding.svelte';
import Admin from './components/Admin.svelte';
import Messages from './components/Messages.svelte';

import { connect, isConnected, isAuthenticated, isOnboarded, user } from './store';

connect();
</script>

<main class="v-screen h-screen flex flex-col">
	{#if $isConnected}
		{#if $isAuthenticated}
			{#if $isOnboarded}
				<Router basepath="/frontend">
					<MainNav/>
					<div class="flex-1 overflow-hidden">
						<Route path='/room/:rid' let:params><Room rid={params.rid}/></Route>
						<Route path='/profile'><Profile/></Route>
					</div>
					<Messages/>
					<Overlay/>
					<Schedule/>
					{#if $user.roles.indexOf('admin') >= 0}
						<Admin/>
					{/if}
				</Router>
			{:else}
				<Onboarding/>
			{/if}
		{:else}
			<Authentication/>
		{/if}
	{:else}
		<ConnectionStatus/>
	{/if}
</main>

<style global lang="postcss">
@tailwind base;
@tailwind components;
@tailwind utilities;
</style>
