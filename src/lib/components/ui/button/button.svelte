<script lang="ts">
  import { cn } from "$lib/utils/utils";
  import { buttonVariants } from "./index.js";
  import type { Snippet } from 'svelte';

  let { variant = '', size = 'default', class: className = undefined, children, ...rest }: {
    variant?: string;
    size?: string;
    class?: string | undefined;
    children?: Snippet;
    [key: string]: any;
  } = $props();

  let classes = $derived(cn(
    buttonVariants.base,
    buttonVariants.variants.variant[variant as keyof typeof buttonVariants.variants.variant],
    buttonVariants.variants.size[size as keyof typeof buttonVariants.variants.size],
    className
  ));
</script>

<button
	class={classes}
	type="button"
	{...rest}
>
	{@render children?.()}
</button>
