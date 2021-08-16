<script lang="ts">
    export let type = 'text';
    export let value: string | boolean;
    export let values = [] as string[];
    export let keyPropagation = false;
    export let error = '';

    function changeValue(ev: Event) {
        if (type === 'checkbox' || type === 'radio') {
            value = (ev.target as HTMLInputElement).checked;
        } else if (type === 'textarea') {
            value = (ev.target as HTMLTextAreaElement).value;
        } else {
            value = (ev.target as HTMLInputElement).value
        }
    }

    function stopPropagation(ev: KeyboardEvent) {
        if (!keyPropagation) {
            ev.stopPropagation();
        }
    }
</script>

{#if type === 'checkbox' || type === 'radio'}
    <label class="block mb-4">
        <input type={type} on:change={changeValue} checked={value}/><span class="inline-block uppercase tracking-wider text-sm pl-2 pb-1"><slot></slot></span>
        {#if error !== ''}
            <span class="block pt-1 text-red-600 text-sm">{error}</span>
        {/if}
    </label>
{:else if type === 'textarea'}
    <label class="block mb-4"><slot></slot>
        <textarea on:change={changeValue} on:keydown={stopPropagation} on:keyup={stopPropagation} class="border-1 border-gray-200 text-black px-2 py-2 w-full h-40 focus:shadow-inner whitespace-pre-wrap">{value}</textarea>
        {#if error !== ''}
            <span class="block pt-1 text-red-600 text-sm">{error}</span>
        {/if}
    </label>
{:else if type === 'select'}
    <label class="block mb-4"><slot></slot>
        <select class="border-1 border-gray-200 text-black px-2 py-2 w-full" on:blur={changeValue} on:change={changeValue}>
            {#each values as option_value}
                <option value={option_value} selected={option_value === value ? 'selected' : null}>{option_value}</option>
            {/each}
        </select>
    </label>
{:else}
    <label class="block mb-4">
        <span class="block uppercase tracking-wider text-sm pb-1"><slot></slot></span><input type={type} value={value} on:change={changeValue} class="block border-1 border-gray-200 text-black px-2 py-2 w-full focus:shadow-inner"/>
        {#if error !== ''}
            <span class="block pt-1 text-red-600 text-sm">{error}</span>
        {/if}
    </label>
{/if}
