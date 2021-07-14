<script lang="ts">
    let cls = '';
    export { cls as class};
</script>

<div role="dialog" class="fixed left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 border-1 border-gray-400 p-4 w-screen sm:w-dialog h-screen sm:h-auto sm:max-h-screen flex flex-col shadow-xl {cls}">
    <div><h2 class="border-b-3 border-yellow-300 font-medium text-xl uppercase tracking-wider pb-2 mb-3"><slot name="title"></slot></h2></div>
    <div class="flex-1 overflow-auto relative"><slot name="content"></slot></div>
    {#if $$slots.actions}
        <div class="text-right border-t-1 border-yellow-300 pt-4"><slot name="actions"></slot></div>
    {/if}
</div>
