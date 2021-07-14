<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import { overlay, user, sendMessage } from '../store';
    import CloseOverlay from './CloseOverlay.svelte';
    import Dialog from './Dialog.svelte';

    let jmApi = null;
    let parent = null;

    onMount(() => {
        const options = {
            roomName: $overlay.url,
            width: '100%',
            height: '100%',
            parentNode: parent,
            userInfo: {
                displayName: $user.name,
                email: $user.email,
            },
            configOverwrite: {
                enableWelcomePage: false,
                disableProfile: true,
                prejoinPageEnabled: false,
            },
        };
        if ($overlay.jwt) {
            options.jwt = $overlay.jwt;
        }
        jmApi = new JitsiMeetExternalAPI('jitsi.meet.room3b.eu', options);
        jmApi.addEventListener('participantRoleChanged', function(event) {
            if (event.role === 'moderator') {
                jmApi.executeCommand('password', $overlay.password);
                if ($overlay.subject) {
                    jmApi.executeCommand('subject', $overlay.subject);
                }
                jmApi.addEventListener('videoConferenceLeft', () => {
                    overlay.set(null);
                });
            }
        });
        jmApi.on('passwordRequired', function () {
            jmApi.executeCommand('password', $overlay.password);
            setTimeout(() => {
                jmApi.addEventListener('videoConferenceLeft', () => {
                    overlay.set(null);
                });
            }, 5000);
        });
    });

    onDestroy(() => {
        if (jmApi) {
            sendMessage({
                type: 'leave-jitsi-room',
            });
            jmApi.executeCommand('hangup');
            jmApi.dispose();
            jmApi = null;
        }
    })
</script>

<Dialog class="z-10 bg-white">
    <span slot="title">{#if $overlay && $overlay.subject}{$overlay.subject}{:else}Video chat{/if} loading...</span>
</Dialog>
<div bind:this={parent} class="absolute top-0 left-0 w-screen h-screen z-20">
    <CloseOverlay/>
</div>
