<script type="ts">
    import { tick, onDestroy } from 'svelte';
    import { writable, derived } from 'svelte/store';

    import { messages, badges, sendMessage, isOnboarding, timezones, onboardingCompleted, coreConfig } from '../store';
    import Dialog from './Dialog.svelte';
    import Button from './Button.svelte';
    import InputField from './InputField.svelte';

    const WELCOME = 0;
    const AVATAR = 1;
    const AVATAR_PHOTO = 2;
    const AVATAR_UPLOAD = 3;
    const TIMEZONE = 4;
    const BADGES = 5;
    const COMPLETE = 6;

    const step = writable(WELCOME);
    let videoWrapperElement = null as HTMLElement;
    let videoElement = null as HTMLVideoElement;
    let canvasElement = null as HTMLCanvasElement;
    let avatarData = null;
    let videoStream = null;
    let fileUploadElement = null as HTMLInputElement;
    let uploading = false;
    let uploadFailed = false;
    let badgeSelection = Object.fromEntries($badges.map((badge) => {
        if (badge.self_assigned) {
            return [badge.role, false];
        } else {
            return null;
        }
    }).filter((value) => { return value !== null; }));
    let timezone = '';

    const editableBadges = derived(badges, (badges) => {
        return badges.filter((badge) => { return badge.self_assigned; });
    }, []);

    const unsubscribeStep = step.subscribe((step) => {
        if (step === AVATAR_PHOTO) {
            tick().then(() => {
                navigator.mediaDevices.getUserMedia({ video: true, audio: false }).then(function(stream) {
                    videoStream = stream;
                    videoElement.srcObject = stream;
                    videoElement.play();
                }).catch(function(err) {
                    console.log("An error occurred: " + err);
                });
            });
        } else if (step === AVATAR) {
            if (videoStream) {
                videoStream.getTracks()[0].stop();
            }
        }
    });

    const unsubscribeMessages = messages.subscribe((message) => {
        if (message.type === 'avatar-image-updated') {
            uploading = false;
            step.set(TIMEZONE);
        } else if (message.type === 'avatar-image-update-failed') {
            uploading = false;
            uploadFailed = true;
        }
    });

    function takeAvatarPhoto() {
        const width = 192 / videoWrapperElement.clientWidth * videoElement.videoWidth;
        const height = 192 / videoWrapperElement.clientHeight * videoElement.videoHeight;
        canvasElement.setAttribute('width', width + 'px');
        canvasElement.setAttribute('height', height + 'px');
        const context = canvasElement.getContext('2d');
        context.drawImage(videoElement, -(videoElement.videoWidth / 2) + (width / 2), -(videoElement.videoHeight / 2) + (height / 2), videoElement.videoWidth, videoElement.videoHeight);
        avatarData = canvasElement.toDataURL('image/png');
    }

    function saveAvatar() {
        if (!uploading) {
            uploading = true;
            uploadFailed = false;
            if (videoStream) {
                videoStream.getTracks()[0].stop();
            }
            sendMessage({
                type: 'update-avatar-image',
                payload: {
                    imageData: avatarData
                }
            });
        }
    }

    function uploadPhoto() {
        function uploadFileChanged(ev: Event) {
            if (fileUploadElement.files.length > 0) {
                const file = fileUploadElement.files[0];
                if (file.type && (file.type === 'image/jpeg' || file.type === 'image/png')) {
                    const reader = new FileReader();
                    reader.addEventListener('load', (event) => {
                        avatarData = event.target.result;
                    });
                    reader.readAsDataURL(file);
                }
            }
            fileUploadElement.value = '';
            fileUploadElement.removeEventListener('change', uploadFileChanged);
        }

        fileUploadElement.addEventListener('change', uploadFileChanged);
        fileUploadElement.click();
    }

    function setTimezone(ev: Event) {
        ev.preventDefault();
        sendMessage({
            'type': 'update-user-profile',
            'payload': {
                'timezone': timezone,
            }
        });
        if ($editableBadges.length > 0) {
            step.set(BADGES);
        } else {
            step.set(COMPLETE);
        }
    }

    function setBadges(ev: Event) {
        ev.preventDefault();
        const roles = Object.entries(badgeSelection).map(([role, selected]) => {
            if (selected) {
                return role;
            } else {
                return null;
            }
        }).filter((role) => { return role !== null; });
        sendMessage({
            'type': 'update-user-profile',
            'payload': {
                'roles': roles,
            }
        });
        step.set(COMPLETE);
    }

    function enter() {
        sendMessage({
            type: 'get-user'
        });
        onboardingCompleted();
    }

    onDestroy(() => {
        unsubscribeStep();
        unsubscribeMessages();
    });
</script>

<div class="w-screen h-screen bg-gray-700">
    {#if $isOnboarding}
        {#if $step === WELCOME}
            <Dialog class="bg-white">
                <span slot="title">Welcome to {$coreConfig.title}</span>
                <div slot="content">
                    <p class="mb-3">We just need to go through a few small setup steps before you can enter {$coreConfig.title}.</p>
                </div>
                <div slot="actions">
                    <Button on:click={() => { step.set(AVATAR); }} type="primary">Get started</Button>
                </div>
            </Dialog>
        {:else if $step === AVATAR}
            <Dialog class="bg-white">
                <span slot="title">Setup your avatar (1/3)</span>
                <div slot="content">
                    <p class="mb-3">First we need to setup your avatar. We can take a photo with your webcam or you can <button on:click={() => { step.set(AVATAR_UPLOAD); }}>upload an avatar image</button>.</p>
                </div>
                <div slot="actions">
                    <Button on:click={() => { step.set(AVATAR_UPLOAD); }} type="secondary">Upload an avatar</Button>
                    <Button on:click={() => { step.set(AVATAR_PHOTO); }} type="primary">Take a photo</Button>
                </div>
            </Dialog>
        {:else if $step === AVATAR_PHOTO}
            <Dialog class="bg-white">
                <span slot="title">{#if avatarData}Setup your avatar (3/3){:else}Setup your avatar (2/3){/if}</span>
                <div slot="content">
                    {#if !videoStream}
                        <p class="mb-3">Please allow {$coreConfig.title} to access your camera.</p>
                    {/if}
                    <div bind:this={videoWrapperElement}>
                        <video bind:this={videoElement} style="clip-path: circle(96px at center)">Video stream not available</video>
                    </div>
                    <canvas bind:this={canvasElement} class="sr-only"></canvas>
                    {#if avatarData}
                        <div class="absolute left-0 top-0 w-full h-full bg-white">
                            {#if uploadFailed}
                                <p class="text-red-500 mb-2">Unfortunately your upload failed. Please take another photo and try again.</p>
                            {/if}
                            <p>If you are happy with your avatar photo, then click on the "Use as avatar" button, otherwise click on the "Take another photo" button to take another photo.</p>
                            <div class="text-center my-2">
                                <div class="inline-block relative">
                                    <img src={avatarData} style="width:192px;height:192px;clip-path:circle(96px at center);" alt="" />
                                    <div class="absolute left-0 top-0 w-full h-full border-4 border-yellow-300 rounded-full"></div>
                                </div>
                                <div class="inline-block relative">
                                    <img src={avatarData} style="width:48px;height:48px;clip-path:circle(24px at center);" alt="" />
                                    <div class="absolute left-0 top-0 w-full h-full border-2 border-yellow-300 rounded-full"></div>
                                </div>
                            </div>
                            <p>You can always change your avatar later.</p>
                        </div>
                    {/if}
                </div>
                <div slot="actions" class="flex">
                    {#if avatarData}
                        <Button on:click={() => { step.set(AVATAR); }} type="secondary" class="flex-0">Back</Button>
                        <div class="flex-1"></div>
                        <Button on:click={() => { avatarData = null; }} type="secondary" class="flex-0 mr-2">Take another photo</Button>
                        <Button on:click={saveAvatar} type="primary" class="flex-0 flex items-center">
                            <span>Use as avatar</span>
                            {#if uploading}
                                <svg viewBox="0 0 24 24" class="ml-2 w-4 h-4 animate-spin">
                                    <path fill="currentColor" d="M19,8L15,12H18A6,6 0 0,1 12,18C11,18 10.03,17.75 9.2,17.3L7.74,18.76C8.97,19.54 10.43,20 12,20A8,8 0 0,0 20,12H23M6,12A6,6 0 0,1 12,6C13,6 13.97,6.25 14.8,6.7L16.26,5.24C15.03,4.46 13.57,4 12,4A8,8 0 0,0 4,12H1L5,16L9,12" />
                                </svg>
                            {/if}
                        </Button>
                    {:else if videoStream}
                        <Button on:click={() => { step.set(AVATAR); }} type="secondary" class="flex-0">Back</Button>
                        <div class="flex-1"></div>
                        <Button on:click={takeAvatarPhoto} type="primary" class="flex-0">Take a photo</Button>
                    {/if}
                </div>
            </Dialog>
        {:else if $step === AVATAR_UPLOAD}
            <Dialog class="bg-white">
                <span slot="title">Setup your avatar ({#if avatarData}3{:else}2{/if}/3)</span>
                <div slot="content">
                    {#if uploadFailed}
                        <p class="text-red-500 mb-2">Unfortunately your upload failed. Please make sure you upload a valid PNG or JPEG image.</p>
                    {/if}
                    {#if avatarData}
                        <p>If you are happy with your avatar, then click on the "Use as avatar" button, otherwise click on the "Upload another photo" button to upload another photo.</p>
                        <div class="text-center my-2">
                            <div class="inline-block relative">
                                <img src={avatarData} style="width:192px;height:192px;clip-path:circle(96px at center);" alt="" />
                                <div class="absolute left-0 top-0 w-full h-full border-4 border-yellow-300 rounded-full"></div>
                            </div>
                            <div class="inline-block relative">
                                <img src={avatarData} style="width:48px;height:48px;clip-path:circle(24px at center);" alt="" />
                                <div class="absolute left-0 top-0 w-full h-full border-2 border-yellow-300 rounded-full"></div>
                            </div>
                        </div>
                        <p class="mb-2">You can always change your avatar later.</p>
                    {:else}
                        <p>The photo you upload must be a PNG or JPEG image and must be square.</p>
                        <div class="text-center mt-8 mb-12">
                            <Button on:click={uploadPhoto} type="primary">Upload a photo</Button>
                        </div>
                    {/if}
                    <input bind:this={fileUploadElement} type="file" class="hidden" accept="image/jpeg,image/png,*.png,*.jpg,*.jpeg"/>
                </div>
                <div slot="actions" class="flex">
                    <Button on:click={() => { step.set(AVATAR); }} type="secondary" class="flex-0">Back</Button>
                    <div class="flex-1"></div>
                    {#if avatarData}
                        <Button on:click={uploadPhoto} type="secondary" class="flex-0 mr-2">Upload another photo</Button>
                        <Button on:click={saveAvatar} type="primary" class="flex-0 flex items-center">
                            <span>Use as avatar</span>
                            {#if uploading}
                                <svg viewBox="0 0 24 24" class="ml-2 w-4 h-4 animate-spin">
                                    <path fill="currentColor" d="M19,8L15,12H18A6,6 0 0,1 12,18C11,18 10.03,17.75 9.2,17.3L7.74,18.76C8.97,19.54 10.43,20 12,20A8,8 0 0,0 20,12H23M6,12A6,6 0 0,1 12,6C13,6 13.97,6.25 14.8,6.7L16.26,5.24C15.03,4.46 13.57,4 12,4A8,8 0 0,0 4,12H1L5,16L9,12" />
                                </svg>
                            {/if}
                        </Button>
                    {/if}
                </div>
            </Dialog>
            {:else if $step === TIMEZONE}
            <Dialog class="bg-white">
                <span slot="title">Select your Timezone</span>
                <div slot="content">
                    <p class="mb-4">Please select your timezone. This is used to show you all times in your local timezone.</p>
                    <InputField type="select" bind:value={timezone} values={$timezones}>Your Timezone</InputField>
                </div>
                <div slot="actions" class="flex">
                    <div class="flex-1"></div>
                    <Button on:click={setTimezone} type="primary" class="flex-0">Set timezone</Button>
                </div>
            </Dialog>
        {:else if $step === BADGES}
            <Dialog class="bg-white">
                <span slot="title">Give yourself some badges</span>
                <div slot="content">
                    <p class="mb-4">If you want to, you can indicate certain things about you by selecting from the badges listed below. This is completely optional and if you don't want to badge yourself, then simply don't select any badges. You can always change these later from your profile page.</p>
                    {#each $editableBadges as badge}
                        <InputField type="checkbox" bind:value={badgeSelection[badge.role]}><img src={badge.url} alt="" class="inline"/> {badge.title}</InputField>
                    {/each}
                </div>
                <div slot="actions" class="flex">
                    <Button on:click={() => { step.set(COMPLETE); }} type="secondary" class="flex-0">No badges, thank you</Button>
                    <div class="flex-1"></div>
                    <Button on:click={setBadges} type="primary" class="flex-0">Set badges</Button>
                </div>
            </Dialog>
        {:else if $step === COMPLETE}
            <Dialog class="bg-white">
                <span slot="title">Enter {$coreConfig.title}</span>
                <div slot="content">
                    <p class="mb-2">You are all set up. When you enter {$coreConfig.title} you can move your avatar around the rooms using the cursor keys.</p>
                    <p class="mb-2">Some areas in the rooms have actions. When you move into such an area, a text describing the action is shown at the bottom of the screen. Press the Enter or Space key to run the action.</p>
                </div>
                <div slot="actions">
                    <Button on:click={enter} type="primary">Enter now</Button>
                </div>
            </Dialog>
        {/if}
    {:else}
        <Dialog class="bg-white">
            <span slot="title">Entering {$coreConfig.title}</span>
        </Dialog>
    {/if}
</div>
