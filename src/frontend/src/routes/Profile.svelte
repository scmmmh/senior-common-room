<script lang="ts">
    import { onDestroy, tick } from 'svelte';
    import { writable, derived } from 'svelte/store';

    import { user, sendMessage, messages, badges, timezones } from '../store';
    import InputField from '../components/InputField.svelte';
    import Button from '../components/Button.svelte';
    import Dialog from '../components/Dialog.svelte';

    const AVATAR = 1;
    const AVATAR_PHOTO = 2;
    const AVATAR_UPLOAD = 3;

    const step = writable(AVATAR);
    let videoWrapperElement = null as HTMLElement;
    let videoElement = null as HTMLVideoElement;
    let canvasElement = null as HTMLCanvasElement;
    let avatarData = null;
    let videoStream = null;
    let fileUploadElement = null as HTMLInputElement;
    let uploading = false;
    let uploadFailed = false;
    let name = $user.name;
    let email = $user.email;
    let timezone = $user.timezone;
    let selectedBadges = Object.fromEntries($badges.map((badge) => {
        if (badge.self_assigned) {
            return [badge.role, $user.roles.indexOf(badge.role) >= 0];
        } else {
            return null;
        }
    }).filter((value) => { return value !== null; }));
    let updateSentTimeout = null;
    let updateAvatar = false;

    function updateProfile(ev: Event) {
        ev.preventDefault();
        let roles = $user.roles;
        Object.entries(selectedBadges).forEach(([role, selected]) => {
            if (selected) {
                if (roles.indexOf(role) < 0) {
                    roles.push(role);
                }
            } else {
                if (roles.indexOf(role) >= 0) {
                    roles.splice(roles.indexOf(role), 1);
                }
            }
        });
        sendMessage({
            'type': 'update-user-profile',
            'payload': {
                'name': name,
                'email': email,
                'timezone': timezone,
                'roles': roles,
            }
        });
        updateSentTimeout = window.setTimeout(() => {
            updateSentTimeout = null;
        }, 5000);
    }

    function dontUpdateProfile(ev: Event) {
        ev.preventDefault();
        name = $user.name;
        email = $user.email;
        timezone = $user.timezone;
        selectedBadges = Object.fromEntries($badges.map((badge) => {
            if (badge.self_assigned) {
                return [badge.role, $user.roles.indexOf(badge.role) >= 0];
            } else {
                return null;
            }
        }).filter((value) => { return value !== null; }));
    }

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
            avatarData = null;
        }
    });

    const unsubscribeMessages = messages.subscribe((message) => {
        if (message.type === 'avatar-image-updated') {
            uploading = false;
            updateAvatar = false;
            sendMessage({
                type: 'get-user'
            });
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

    const editableBadges = derived(badges, (badges) => {
        return badges.filter((badge) => { return badge.self_assigned; });
    }, []);

    onDestroy(() => {
        unsubscribeStep();
        unsubscribeMessages();
    });
</script>

<div class="v-full h-full overflow-auto bg-gray-800 py-4">
    <div class="container mx-auto bg-gray-700 text-white h-full rounded px-3 py-2">
        <h1 class="text-2xl tracking-widest">My Profile</h1>
        <div class="flex pt-4">
            <div class="flex-0">
                <div class="relative">
                    <img src={$user.avatar + '-large.png'} alt="" style="max-width: 16rem;"/>
                    <Button type="icon" class="absolute bottom-0 right-0" on:click={() => { step.set(AVATAR); updateAvatar = true; }}>
                        <svg viewBox="0 0 24 24" class="w-6 h-6">
                            <path fill="currentColor" d="M20.71,7.04C21.1,6.65 21.1,6 20.71,5.63L18.37,3.29C18,2.9 17.35,2.9 16.96,3.29L15.12,5.12L18.87,8.87M3,17.25V21H6.75L17.81,9.93L14.06,6.18L3,17.25Z" />
                        </svg>
                    </Button>
                </div>
            </div>
            <form class="flex-1 pl-10 max-w-lg" on:submit={updateProfile}>
                <InputField type="text" bind:value={name}>Name</InputField>
                <InputField type="text" bind:value={email}>E-Mail Address</InputField>
                <InputField type="select" bind:value={timezone} values={$timezones}>Your Timezone</InputField>
                {#if $editableBadges.length > 0}
                    <span class="block uppercase tracking-wider text-sm pb-1">Badges</span>
                    {#each $editableBadges as badge}
                        <InputField type="checkbox" bind:value={selectedBadges[badge.role]}><img src={badge.url} alt="" class="inline"/> {badge.title}</InputField>
                    {/each}
                {/if}
                <div class="pt-4 text-right">
                    <Button type="secondary" on:click={dontUpdateProfile}>Don't Update</Button>
                    <Button type="primary">
                        {#if updateSentTimeout !== null}
                            <svg viewBox="0 0 24 24" class="w-5 h-5 inline">
                                <path fill="currentColor" d="M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z" />
                            </svg>
                        Updated
                        {:else}
                            Update
                        {/if}
                    </Button>
                </div>
            </form>
        </div>
    </div>
    {#if updateAvatar}
        <div class="fixed left-0 top-0 w-screen h-screen bg-gray-800 bg-opacity-60">
            {#if $step === AVATAR}
                <Dialog class="bg-white">
                    <span slot="title">Update your avatar (1/3)</span>
                    <div slot="content">
                        <p class="mb-3">We can <button on:click={() => { step.set(AVATAR_PHOTO); }}>take a photo</button> with your webcam or you can <button on:click={() => { step.set(AVATAR_UPLOAD); }}>upload an avatar image</button>.</p>
                    </div>
                    <div slot="actions" class="flex">
                        <Button type="secondary" on:click={() => { updateAvatar = false; }}>Don't Update</Button>
                        <div class="flex-1"></div>
                        <Button on:click={() => { step.set(AVATAR_UPLOAD); }} type="primary" class="mr-2">Upload an avatar</Button>
                        <Button on:click={() => { step.set(AVATAR_PHOTO); }} type="primary">Take a photo</Button>
                    </div>
                </Dialog>
            {:else if $step === AVATAR_PHOTO}
                <Dialog class="bg-white">
                    <span slot="title">{#if avatarData}Update your avatar (3/3){:else}Update your avatar (2/3){/if}</span>
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
                            <Button type="secondary" on:click={() => { updateAvatar = false; }}>Don't Update</Button>
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
                            <Button type="secondary" on:click={() => { updateAvatar = false; }}>Don't Update</Button>
                            <div class="flex-1"></div>
                            <Button on:click={takeAvatarPhoto} type="primary" class="flex-0">Take a photo</Button>
                        {/if}
                    </div>
                </Dialog>
            {:else if $step === AVATAR_UPLOAD}
                <Dialog class="bg-white">
                    <span slot="title">Updated your avatar ({#if avatarData}3{:else}2{/if}/3)</span>
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
                        <Button type="secondary" on:click={() => { updateAvatar = false; }}>Don't Update</Button>
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
            {/if}
        </div>
    {/if}
</div>
