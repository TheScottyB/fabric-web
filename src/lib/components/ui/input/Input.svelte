<script lang="ts">
  import { cn } from "$lib/utils/utils";

  let { value = $bindable(''), placeholder = undefined, id = undefined, disabled = false, required = false, class: className = undefined, ...rest }: {
    value?: string;
    placeholder?: string | undefined;
    id?: string | undefined;
    disabled?: boolean;
    required?: boolean;
    class?: string | undefined;
    [key: string]: any;
  } = $props();
</script>

<input
  type="text"
  {id}
  bind:value
  {placeholder}
  {disabled}
  {required}
  class={cn(
    "block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm disabled:cursor-not-allowed disabled:opacity-50",
    className
  )}
  {...rest}
/>
