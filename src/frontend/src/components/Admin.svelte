<script lang="ts">
    import Button from './Button.svelte';
    import Modal from './Modal.svelte';
    import Dialog from './Dialog.svelte';
    import InputField from './InputField.svelte';
    import { sendMessage } from '../store';

    let visible = false;

    let showSendBroadcast = false;
    let broadcastMessage = '';
    let broadcastError = '';

    function sendBroadcastMessage(ev) {
        console.log('hm');
        ev.preventDefault();
        if (broadcastMessage.trim() !== '') {
            sendMessage({
                type: 'broadcast-message',
                payload: {
                    message: broadcastMessage.trim(),
                }
            });
            broadcastError = '';
            showSendBroadcast = false;
            visible = false;
        } else {
            broadcastError = 'Please provide a message';
        }
    }
</script>

<div class="fixed right-0 top-20 z-50">
    <div class="bg-gray-700 text-white rounded-l-lg py-4 pl-4 pr-2">
        <h2 class="sr-only">Administration</h2>
        <div class="{visible ? 'mb-4' : ''}">
            <button on:click={() => { visible = !visible; }} aria-label={visible ? 'Hide administration functions' : 'Show administration functions'}>
                <svg viewBox="0 0 24 24" class="w-8 h-8">
                    <path fill="currentColor" d="M16.5,12A2.5,2.5 0 0,0 19,9.5A2.5,2.5 0 0,0 16.5,7A2.5,2.5 0 0,0 14,9.5A2.5,2.5 0 0,0 16.5,12M9,11A3,3 0 0,0 12,8A3,3 0 0,0 9,5A3,3 0 0,0 6,8A3,3 0 0,0 9,11M16.5,14C14.67,14 11,14.92 11,16.75V19H22V16.75C22,14.92 18.33,14 16.5,14M9,13C6.67,13 2,14.17 2,16.5V19H9V16.75C9,15.9 9.33,14.41 11.37,13.28C10.5,13.1 9.66,13 9,13Z" />
                </svg>
            </button>
        </div>
        {#if visible}
            <nav>
                <ul>
                    <li><Button type="primary-outline" on:click={() => { broadcastMessage = ''; showSendBroadcast = true; }}>Send broadcast message</Button></li>
                </ul>
            </nav>
            {#if showSendBroadcast}
                <form on:submit={sendBroadcastMessage}>
                    <Modal let:close={modalClose} on:close={() => { showSendBroadcast = false; }}>
                        <Dialog class="bg-white text-black">
                            <span slot="title">Send a broadcast message</span>
                            <div slot="content">
                                <InputField type="textarea" bind:value={broadcastMessage} error={broadcastError}>
                                    Broadcast message to send
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
        {/if}
    </div>
</div>
