<script lang="ts">
    export let type = 'text';
    export let value: string | boolean;
    export let error = '';

    function changeValue(ev: Event) {
        if (type === 'checkbox' || type === 'radio') {
            value = (ev.target as HTMLInputElement).checked;
        } else {
            value = (ev.target as HTMLInputElement).value
        }
    }
</script>

{#if type === 'checkbox' || type === 'radio'}
    <label class="block mb-4">
        <input type={type} on:change={changeValue} checked={value}/><span class="inline-block uppercase tracking-wider text-sm pl-2 pb-1"><slot></slot></span>
        {#if error !== ''}
            <span>{error}</span>
        {/if}
    </label>
{:else}
    <label class="block mb-4">
        <span class="block uppercase tracking-wider text-sm pb-1"><slot></slot></span><input type={type} value={value} on:change={changeValue} class="block border-1 border-gray-200 px-2 py-2 w-full focus:shadow-inner"/>
        {#if error !== ''}
            <span class="block pt-1 text-red-600 text-sm">{error}</span>
        {/if}
    </label>
{/if}
