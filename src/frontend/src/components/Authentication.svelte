<script lang="ts">
    import { onDestroy } from 'svelte';

    import { authenticate, isAuthenticating, isAuthenticationTokenSent, isAuthenticationFailed, messages } from '../store';
    import Dialog from './Dialog.svelte';
    import InputField from './InputField.svelte';
    import Button from './Button.svelte';

    let email = '';
    let emailError = '';
    let remember = true;

    function login(ev: Event) {
        ev.preventDefault();
        authenticate(email, remember);
    }

    const unsubscribe = messages.subscribe((message) => {
        if (message.type === 'authentication-failed') {
            if (message.payload && message.payload.email) {
                emailError = message.payload.email;
            }
        }
    });

    onDestroy(unsubscribe);
</script>

<div class="w-screen h-screen bg-gray-700">
    {#if $isAuthenticationTokenSent}
        <Dialog class="bg-white">
            <span slot="title" class="flex">
                <span class="flex-1">Authentication Link Sent</span>
                <svg viewBox="0 0 24 24" class="flex-0 w-6 text-green-700">
                    <path fill="currentColor" d="M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z" />
                </svg>
            </span>
            <div slot="content">
                <p class="mb-3">An authentication link has been sent to the e-mail address. Please also check your spam folder. The authentication link is valid for a single login.</p>
            </div>
        </Dialog>
    {:else}
        <form on:submit={login}>
            <Dialog class="bg-white">
                <span slot="title">Login</span>
                <div slot="content">
                    <InputField type="email" error={$isAuthenticationFailed ? emailError : ''} bind:value={email}>E-Mail</InputField>
                    <InputField type="checkbox" bind:value={remember}>Remember Me</InputField>
                </div>
                <div slot="actions">
                    {#if !$isAuthenticating}
                        <Button type="primary">E-Mail Login Link</Button>
                    {:else}
                        <Button type="secondary">
                            <span class="flex">
                                <span class="pr-2">Please wait...</span>
                                <svg viewBox="0 0 24 24" class="w-4 animate-spin">
                                    <path fill="currentColor" d="M12,4V2A10,10 0 0,0 2,12H4A8,8 0 0,1 12,4Z" />
                                </svg>
                            </span>
                        </Button>
                    {/if}
                </div>
        </Dialog>
        </form>
    {/if}
</div>
