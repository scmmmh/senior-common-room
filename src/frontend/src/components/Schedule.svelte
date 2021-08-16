<script lang="ts">
    import { derived } from 'svelte/store';
    import { Link } from 'svelte-navigator';

    import { schedule, rooms, showSchedule } from '../store';
    import Dialog from './Dialog.svelte';
    import Modal from './Modal.svelte';
    import Button from './Button.svelte';

    const groupedEntries = derived(schedule, (schedule) => {
        let lastDate = '';
        const days = [] as ScheduleConfigPayload[][];
        let times = [];
        schedule.forEach((entry) => {
            if (entry.start_date !== lastDate) {
                if (times.length > 0) {
                    days.push(times);
                    times = [];
                }
                lastDate = entry.start_date;
            }
            times.push(entry);
        });
        if (times.length > 0) {
            days.push(times);
        }
        return days;
    }, []);

    const roomsDict = derived(rooms, (rooms) => {
        return Object.fromEntries(rooms.map((room) => {
            return [room.slug, room];
        }));
    }, {});

    function closeSchedule(ev: Event) {
        if (ev) {
            ev.preventDefault();
        }
        showSchedule.set(false);
    }

    function splitDescription(description: string) {
        return description.split('\n');
    }
</script>

{#if $showSchedule}
    <Modal on:close={closeSchedule}>
        <Dialog>
            <div slot="title">Schedule</div>
            <div slot="content">
                {#each $groupedEntries as days}
                    <h2 class="text-xl tracking-wider mt-4 mb-2">{days[0].start_date}</h2>
                    <table>
                        <thead>
                            <tr class="sr-only">
                                <th class="py-2 px-3">Time</th>
                                <th class="py-2 px-3">Event</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each days as entry}
                                <tr>
                                    <td class="py-2 px-3 align-top">{entry.start_time} - {entry.end_time}{#if entry.day_diff !== 0}<span class="pl-1 text-xs">(+{entry.day_diff} day)</span>{/if}</td>
                                    <td class="py-2 px-3 align-top">
                                        <p class="font-bold tracking-widest">{entry.title}</p>
                                        {#if entry.room && $roomsDict[entry.room]}
                                            <p><Link to={'/room/' + $roomsDict[entry.room].slug} class="underline">{$roomsDict[entry.room].label}</Link></p>
                                        {/if}
                                        {#if entry.description}
                                            {#each splitDescription(entry.description) as para}
                                                <p class="text-sm">{@html para}</p>
                                            {/each}
                                        {/if}
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                {/each}
            </div>
            <div slot="actions">
                <Button on:click={closeSchedule} type="primary">Close</Button>
            </div>
        </Dialog>
    </Modal>
{/if}
