<script lang="ts">
  import { onMount } from 'svelte';
  import { Select } from "$lib/components/ui/select";
  import { patterns, patternAPI, systemPrompt, selectedPatternName } from "$lib/store/pattern-store";
  import { get } from 'svelte/store';

  let selectedPreset = $state($selectedPatternName || "");

  // Subscribe to selectedPatternName changes (replaces manual .subscribe())
  $effect(() => {
    const value = $selectedPatternName;
    if (value && value !== selectedPreset) {
      console.log('Pattern selected from modal:', value);
      selectedPreset = value;
    }
  });

  // Watch selectedPreset changes (replaces $: reactive block)
  // Always call selectPattern when the dropdown value changes.
  // The patternAPI.selectPattern function handles empty strings correctly.
  $effect(() => {
    // Track selectedPreset so this effect re-runs when it changes
    const preset = selectedPreset;

    // Log the change regardless of the value
    console.log('Dropdown selection changed to:', preset);
    try {
      // Call the function to select the pattern (or reset if selectedPreset is empty)
      patternAPI.selectPattern(preset);

      // Optional: Keep verification logs if helpful for debugging
      const currentSystemPrompt = get(systemPrompt);
      const currentPattern = get(selectedPatternName);
      console.log('After dropdown selection - Pattern:', currentPattern);
      console.log('After dropdown selection - System Prompt length:', currentSystemPrompt?.length);

      // Optional: Refine verification logic if needed
      // For example, only log error if a pattern was expected but not set
      // if (preset && (!currentPattern || !currentSystemPrompt)) {
      //   console.error('Pattern selection verification failed:');
      //   console.error('- Selected Pattern:', currentPattern);
      //   console.error('- System Prompt:', currentSystemPrompt);
      // }
    } catch (error) {
      // Log any errors during the pattern selection process
      console.error('Error processing pattern selection:', error);
    }
  });

    onMount(async () => {
      await patternAPI.loadPatterns();
    });
</script>

<div class="min-w-0">
  <Select
    bind:value={selectedPreset}
    class="bg-primary-800/30 border-none hover:bg-primary-800/40 transition-colors"
  >
    <option value="">Load a pattern...</option>
    {#each $patterns as pattern}
      <option value={pattern.Name}>{pattern.Name}</option>
    {/each}
  </Select>
</div>
