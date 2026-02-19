<script lang="ts">
  import { chatState, errorStore, streamingStore } from '$lib/store/chat-store';
  import { onMount } from 'svelte';
  import { marked } from 'marked';
  import SessionManager from './SessionManager.svelte';
  import { fade, slide } from 'svelte/transition';
  import { ArrowDown } from 'lucide-svelte';
  import Modal from '$lib/components/ui/modal/Modal.svelte';
  import PatternList from '$lib/components/patterns/PatternList.svelte';
  import type { Message } from '$lib/interfaces/chat-interface';
  import { get } from 'svelte/store';
  import { selectedPatternName } from '$lib/store/pattern-store';

  let showPatternModal = $state(false);
  let messagesContainer: HTMLDivElement | null = $state(null);
  let showScrollButton = $state(false);

  function scrollToBottom() {
    if (messagesContainer) {
      messagesContainer.scrollTo({ top: messagesContainer.scrollHeight, behavior: 'smooth' });
    }
  }

  function handleScroll() {
    if (!messagesContainer) return;
    const { scrollTop, scrollHeight, clientHeight } = messagesContainer;
    showScrollButton = scrollHeight - scrollTop - clientHeight > 100;
  }

  // Auto-scroll when messages change
  $effect(() => {
    if ($chatState.messages.length > 0) {
      setTimeout(scrollToBottom, 100);
    }
  });

  // Auto-scroll when streaming completes
  $effect(() => {
    if ($streamingStore === false) {
      setTimeout(scrollToBottom, 100);
    }
  });

  onMount(() => {
    if (messagesContainer) {
      messagesContainer.addEventListener('scroll', handleScroll);
      return () => {
        if (messagesContainer) {
          messagesContainer.removeEventListener('scroll', handleScroll);
        }
      };
    }
  });

  const renderer = new marked.Renderer();
  marked.setOptions({
    gfm: true,
    breaks: true,
    renderer,
    async: false
  });

  function shouldRenderAsMarkdown(message: Message): boolean {
    const pattern = get(selectedPatternName);
    if (pattern && message.role === 'assistant') {
      return message.format !== 'mermaid';
    }
    return message.role === 'assistant' && message.format !== 'plain';
  }

  function renderContent(message: Message): string {
    const content = message.content.replace(/\\n/g, '\n');

    if (shouldRenderAsMarkdown(message)) {
      try {
        return marked.parse(content, { async: false }) as string;
      } catch {
        return content;
      }
    }
    return content;
  }

  function friendlyError(raw: string): string {
    if (raw.includes('fetch') || raw.includes('network') || raw.includes('ECONNREFUSED')) {
      return 'Unable to reach the server. Check that the Fabric API is running.';
    }
    if (raw.includes('500') || raw.includes('Internal Server Error')) {
      return 'The server encountered an error. Please try again.';
    }
    if (raw.includes('timeout') || raw.includes('ETIMEDOUT')) {
      return 'The request timed out. The server may be busy — try again shortly.';
    }
    return raw;
  }
</script>

<div class="bg-primary-800/30 rounded-lg flex flex-col h-full shadow-lg">
  <div class="flex justify-between items-center p-3 flex-none border-b border-white/5">
    <div>
      <span class="text-xs text-white/70 font-medium">Chat History</span>
    </div>
    <SessionManager />
  </div>

  <Modal
    show={showPatternModal}
    onclose={() => showPatternModal = false}
  >
    <PatternList onclose={() => showPatternModal = false} />
  </Modal>

  {#if $errorStore}
    <div class="error-message" transition:slide>
      <div class="bg-red-900/30 border-l-4 border-red-400 text-red-300 p-3 mx-3 mt-3 rounded text-sm" role="alert">
        <p>{friendlyError($errorStore)}</p>
      </div>
    </div>
  {/if}

  <div
    class="messages-container p-3 flex-1 overflow-y-auto max-h-dvh relative"
    bind:this={messagesContainer}
  >
    <div class="messages-content flex flex-col gap-3">
      {#each $chatState.messages as message}
        <div
          class="message-item {message.role === 'system' ? 'w-full bg-blue-900/20' : message.role === 'assistant' ? 'bg-primary/5 rounded-lg p-3' : 'ml-auto'}"
          transition:fade
          class:loading-message={message.format === 'loading'}
        >
          <div class="message-header flex items-center gap-2 mb-1 {message.role === 'assistant' || message.role === 'system' ? '' : 'justify-end'}">
            <span class="text-xs text-muted-foreground rounded-lg p-1 variant-glass-secondary font-bold uppercase">
              {#if message.role === 'system'}
                SYSTEM
              {:else if message.role === 'assistant'}
                AI
              {:else}
                You
              {/if}
            </span>
            {#if message.role === 'assistant' && $streamingStore}
              <span class="loading-indicator flex gap-1">
                <span class="dot animate-bounce">.</span>
                <span class="dot animate-bounce delay-100">.</span>
                <span class="dot animate-bounce delay-200">.</span>
              </span>
            {/if}
          </div>

          {#if message.role === 'system'}
            <div class="text-blue-300 text-sm font-semibold">
              {message.content}
            </div>
          {:else if message.role === 'assistant'}
            <div class="{shouldRenderAsMarkdown(message) ? 'prose prose-slate dark:prose-invert text-inherit prose-headings:text-inherit prose-pre:bg-primary/10 prose-pre:text-inherit' : 'whitespace-pre-wrap'} text-sm max-w-none">
              {@html renderContent(message)}
            </div>
          {:else}
            <div class="whitespace-pre-wrap text-sm">
              {message.content}
            </div>
          {/if}
        </div>
      {/each}
    </div>
    {#if showScrollButton}
      <button
        class="absolute bottom-4 right-4 bg-primary/20 hover:bg-primary/30 rounded-full p-2 transition-opacity"
        onclick={scrollToBottom}
        transition:fade
      >
        <ArrowDown class="w-4 h-4" />
      </button>
    {/if}
  </div>
</div>

<style>
  :global(.loading-message) {
    animation: flash 1.5s ease-in-out infinite;
  }

  @keyframes flash {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
  }

  .messages-container {
    flex: 1;
    overflow-y: auto;
    scrollbar-width: thin;
    -ms-overflow-style: thin;
  }

  .messages-content {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .message-header {
    display: flex;
    gap: 0.5rem;
  }

  .message-item {
    position: relative;
  }

  .loading-indicator {
    display: inline-flex;
    gap: 2px;
  }

  .dot {
    animation: blink 1.4s infinite;
    opacity: 0;
  }

  .dot:nth-child(2) {
    animation-delay: 0.2s;
  }

  .dot:nth-child(3) {
    animation-delay: 0.4s;
  }

  @keyframes blink {
    0%, 100% { opacity: 0; }
    50% { opacity: 1; }
  }

  :global(.prose pre) {
    background-color: rgb(40, 44, 52);
    color: rgb(171, 178, 191);
    padding: 1rem;
    border-radius: 0.375rem;
    margin: 1rem 0;
  }

  :global(.prose code) {
    color: rgb(171, 178, 191);
    background-color: rgba(40, 44, 52, 0.1);
    padding: 0.2em 0.4em;
    border-radius: 0.25rem;
  }
</style>
