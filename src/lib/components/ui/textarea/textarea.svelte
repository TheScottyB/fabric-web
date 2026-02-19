<script lang="ts">
  import { cn } from '$lib/utils/utils';

  let { value = $bindable(''), readonly = false, class: className = '', ...rest }: {
    value?: string;
    readonly?: boolean;
    class?: string;
    [key: string]: any;
  } = $props();
</script>

<textarea
	class={cn(
		"border-input placeholder:text-muted-foreground focus-visible:ring-ring flex min-h-[60px] w-full rounded-lg border bg-transparent px-3 py-2 text-sm shadow-lg focus-visible:outline-none focus-visible:ring-1 disabled:cursor-not-allowed disabled:opacity-50",
		className
	)}
	bind:value
	{readonly}
	{...rest}
></textarea>
