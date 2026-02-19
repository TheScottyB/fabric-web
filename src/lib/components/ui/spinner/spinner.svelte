<script lang="ts">
  import { cn } from '$lib/utils/utils';
  import { Loader2 } from 'lucide-svelte';

  let { class: className = undefined, ...rest }: {
    class?: string | undefined;
    [key: string]: any;
  } = $props();
</script>

<Loader2 class={cn('h-4 w-4 animate-spin', className)} {...rest} />
