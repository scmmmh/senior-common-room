<script lang="ts">
	import { createEventDispatcher } from 'svelte';

    import { sendMessage } from '../store';
    import Modal from './Modal.svelte';
    import Dialog from './Dialog.svelte';
    import Button from './Button.svelte';
    import InputField from './InputField.svelte';

    export let type;
    export let user = null;

    const dispatch = createEventDispatcher();

    let message = '';
    let messageError = '';

    function submitMessage(ev: Event) {
        ev.preventDefault();
        if (message.trim() !== '') {
            if (type === 'broadcast-message') {
                sendMessage({
                    type: type,
                    payload: {
                        message: message.trim(),
                    }
                });
            } else if (type === 'user-message') {
                sendMessage({
                    type: type,
                    payload: {
                        user: {
                            id: user.id,
                        },
                        message: message.trim(),
                    }
                });
            }
            messageError = '';
            dispatch('close', {
                sent: true
            });
        } else {
            messageError = 'Please provide a message';
        }
    }

    function close() {
        dispatch('close', {
            sent: false
        });
    }
</script>

<form on:submit={submitMessage}>
    <Modal let:close={modalClose} on:close={close}>
        <Dialog>
            <span slot="title"><slot></slot></span>
            <div slot="content">
                <InputField type="textarea" bind:value={message} error={messageError}>
                    Message
                </InputField>
            </div>
            <div slot="actions">
                <Button on:click={(ev) => { ev.preventDefault(); modalClose(); }} type="secondary">Don't Send</Button>
                <Button type="primary">Send</Button>
            </div>
        </Dialog>
    </Modal>
</form>
