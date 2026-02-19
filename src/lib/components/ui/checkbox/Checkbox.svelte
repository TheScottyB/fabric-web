<script lang="ts">
  import { cn } from "$lib/utils/utils";

  let { checked = $bindable(false), id = undefined, disabled = false, class: className = undefined, ...rest }: {
    checked?: boolean;
    id?: string | undefined;
    disabled?: boolean;
    class?: string | undefined;
    [key: string]: any;
  } = $props();
</script>

<div class="flex items-center">
  <input
    type="checkbox"
    {id}
    bind:checked
    {disabled}
    class={cn(
      "h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500 disabled:cursor-not-allowed disabled:opacity-50",
      className
    )}
    {...rest}
  />
</div>
