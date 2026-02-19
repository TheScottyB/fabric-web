<script lang="ts">
  import type { Snippet } from 'svelte';

  let { class: className = '', children, ...rest }: {
    class?: string;
    children?: Snippet;
    [key: string]: any;
  } = $props();
</script>

<label
  class="block text-sm font-medium text-gray-700 dark:text-gray-200 {className}"
  {...rest}
>
  {@render children?.()}
</label>
