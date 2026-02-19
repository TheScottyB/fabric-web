<script lang="ts">
  import { Button } from "$lib/components/ui/button";
  import { Textarea } from "$lib/components/ui/textarea";
  import { sendMessage, messageStore } from '$lib/store/chat-store';
  import { systemPrompt, selectedPatternName } from '$lib/store/pattern-store';
  import { getToastStore } from '@skeletonlabs/skeleton';
  import { FileButton } from '@skeletonlabs/skeleton';
  import { Paperclip, Send } from 'lucide-svelte';
  import { onMount } from 'svelte';
  import { get } from 'svelte/store';
  import { getTranscript } from '$lib/services/transcriptService';
  import { ChatService } from '$lib/services/ChatService';
  import { languageStore } from '$lib/store/language-store';
  import { obsidianSettings, updateObsidianSettings } from '$lib/store/obsidian-store';
  import { PdfConversionService } from '$lib/services/PdfConversionService';

  const pdfService = new PdfConversionService();
  const chatService = new ChatService();
  const toastStore = getToastStore();

  let userInput = $state("");
  let isYouTubeURL = $state(false);
  let files: FileList | undefined = $state(undefined);
  let uploadedFiles: string[] = $state([]);
  let fileContents: string[] = $state([]);
  let isProcessingFiles = $state(false);
  let isFileIndicatorVisible = $state(false);
  let fileButtonKey = $state(false);

  function detectYouTubeURL(input: string): boolean {
    const youtubePattern = /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)/i;
    return youtubePattern.test(input);
  }

  function handleInput(event: Event) {
    const target = event.target as HTMLTextAreaElement;
    userInput = target.value;

    const languageQualifiers: Record<string, string> = {
      '--en': 'en',
      '--fr': 'fr',
      '--es': 'es',
      '--de': 'de',
      '--zh': 'zh',
      '--ja': 'ja'
    };

    for (const [qualifier, lang] of Object.entries(languageQualifiers)) {
      if (userInput.includes(qualifier)) {
        languageStore.set(lang);
        userInput = userInput.replace(new RegExp(`${qualifier}\\s*`), '');
        break;
      }
    }

    isYouTubeURL = detectYouTubeURL(userInput);
  }

  async function handleFileUpload(e: Event) {
    uploadedFiles = [];
    if (!files || files.length === 0) return;

    if (uploadedFiles.length >= 5 || (uploadedFiles.length + files.length) > 5) {
      toastStore.trigger({
        message: 'Maximum 5 files allowed',
        background: 'variant-filled-error'
      });
      return;
    }

    isProcessingFiles = true;
    try {
      messageStore.update(messages => [...messages, {
        role: 'system',
        content: 'Processing files...',
        format: 'loading'
      }]);

      for (let i = 0; i < files.length && uploadedFiles.length < 5; i++) {
        const file = files[i];
        const content = await readFileContent(file);
        fileContents.push(content);
        uploadedFiles = [...uploadedFiles, file.name];

        messageStore.update(messages => {
          const newMessages = [...messages];
          const lastMessage = newMessages[newMessages.length - 1];
          if (lastMessage?.format === 'loading') {
            lastMessage.content = `Processing ${file.name} (${file.type})...`;
          }
          return newMessages;
        });
      }

      messageStore.update(messages =>
        messages.filter(m => m.format !== 'loading')
      );
    } catch (error) {
      toastStore.trigger({
        message: 'Error processing files: ' + (error as Error).message,
        background: 'variant-filled-error'
      });
      messageStore.update(messages =>
        messages.filter(m => m.format !== 'loading')
      );
    } finally {
      isProcessingFiles = false;
    }
  }

  async function readFileContent(file: File): Promise<string> {
    if (file.type === 'application/pdf') {
      try {
        const markdown = await pdfService.convertToMarkdown(file);

        if (!markdown || markdown.trim().length === 0) {
          throw new Error('PDF conversion returned empty content');
        }

        fileContents.push(markdown);

        const enhancedPrompt = `${$systemPrompt}\nAnalyze and process the provided content according to these instructions.`;
        const finalContent = `${userInput}\n\nFile Contents (PDF):\n${markdown}`;
        await sendMessage(finalContent, enhancedPrompt);

        return markdown;
      } catch (error) {
        const errorMessage = error instanceof Error
          ? error.message
          : 'Unknown error during PDF conversion';
        throw new Error(`Failed to convert PDF ${file.name}: ${errorMessage}`);
      }
    }

    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = async (e) => {
        const content = e.target?.result as string;
        const enhancedPrompt = `${$systemPrompt}\nAnalyze and process the provided content according to these instructions.`;
        const finalContent = `${userInput}\n\nFile Contents (Text):\n${content}`;
        await sendMessage(finalContent, enhancedPrompt);
        resolve(content);
      };

      reader.onerror = () => {
        reject(new Error(`Failed to read ${file.name}: ${reader.error?.message}`));
      };

      reader.readAsText(file);
    });
  }

  async function saveToObsidian(content: string) {
    if (!$obsidianSettings.saveToObsidian) return;

    if (!$obsidianSettings.noteName) {
      toastStore.trigger({
        message: 'Please enter a note name in Obsidian settings',
        background: 'variant-filled-error'
      });
      return;
    }

    if (!$selectedPatternName) {
      toastStore.trigger({
        message: 'No pattern selected',
        background: 'variant-filled-error'
      });
      return;
    }

    if (!content) {
      toastStore.trigger({
        message: 'No content to save',
        background: 'variant-filled-error'
      });
      return;
    }

    try {
      const response = await fetch('/obsidian', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pattern: $selectedPatternName,
          noteName: $obsidianSettings.noteName,
          content
        })
      });

      const responseData = await response.json();

      if (!response.ok) {
        throw new Error(responseData.error || 'Failed to save to Obsidian');
      }

      updateObsidianSettings({
        saveToObsidian: false,
        noteName: ''
      });
      toastStore.trigger({
        message: responseData.message || `Saved to Obsidian: ${responseData.fileName}`,
        background: 'variant-filled-success'
      });
    } catch (error) {
      console.error('Failed to save to Obsidian:', error);
      toastStore.trigger({
        message: error instanceof Error ? error.message : 'Failed to save to Obsidian',
        background: 'variant-filled-error'
      });
    }
  }

  async function processYouTubeURL(input: string) {
    const originalLanguage = get(languageStore);

    try {
      messageStore.update(messages => [...messages, {
        role: 'system',
        content: 'Processing YouTube video...',
        format: 'loading'
      }]);

      const { transcript } = await getTranscript(input);

      const stream = await chatService.streamChat(transcript, $systemPrompt);
      await chatService.processStream(
        stream,
        (content, response) => {
          messageStore.update(messages => {
            const newMessages = [...messages];
            const lastMessage = newMessages[newMessages.length - 1];
            if (lastMessage?.format === 'loading') {
              newMessages.pop();
            }
            newMessages.push({
              role: 'assistant',
              content,
              format: response?.format
            });
            return newMessages;
          });
        },
        (error) => {
          messageStore.update(messages =>
            messages.filter(m => m.format !== 'loading')
          );
          throw error;
        }
      );

      if ($obsidianSettings.saveToObsidian) {
        let lastContent = '';
        messageStore.subscribe(messages => {
          const lastMessage = messages[messages.length - 1];
          if (lastMessage?.role === 'assistant') {
            lastContent = lastMessage.content;
          }
        })();
        if (lastContent) await saveToObsidian(lastContent);
      }

      userInput = "";
      uploadedFiles = [];
      fileContents = [];
    } catch (error) {
      console.error('Error processing YouTube URL:', error);
      messageStore.update(messages =>
        messages.filter(m => m.format !== 'loading')
      );
      throw error;
    }
  }

  async function handleSubmit() {
    if (!userInput.trim()) return;

    try {
      const inputText = userInput.trim();

      if (isYouTubeURL) {
        await processYouTubeURL(inputText);
        return;
      }

      messageStore.update(messages => [...messages, {
        role: 'user',
        content: inputText
      }]);

      messageStore.update(messages => [...messages, {
        role: 'system',
        content: 'Processing...',
        format: 'loading'
      }]);

      userInput = "";
      const filesForProcessing = [...uploadedFiles];
      const contentsForProcessing = [...fileContents];
      uploadedFiles = [];
      fileContents = [];
      fileButtonKey = !fileButtonKey;

      const contentWithFiles = contentsForProcessing.length > 0
        ? `${inputText}\n\nFile Contents (${filesForProcessing.map(f => f.endsWith('.pdf') ? 'PDF' : 'Text').join(', ')}):\n${contentsForProcessing.join('\n\n---\n\n')}`
        : inputText;

      const enhancedPrompt = contentsForProcessing.length > 0
        ? `${$systemPrompt}\nAnalyze and process the provided content according to these instructions.`
        : $systemPrompt;

      try {
        const stream = await chatService.streamChat(contentWithFiles, enhancedPrompt);

        await chatService.processStream(
          stream,
          (content, response) => {
            messageStore.update(messages => {
              const newMessages = [...messages];
              const loadingIndex = newMessages.findIndex(m => m.format === 'loading');
              if (loadingIndex !== -1) {
                newMessages.splice(loadingIndex, 1);
              }
              newMessages.push({
                role: 'assistant',
                content,
                format: response?.format
              });
              return newMessages;
            });
          },
          (error) => {
            messageStore.update(messages =>
              messages.filter(m => m.format !== 'loading')
            );
            messageStore.update(messages => [...messages, {
              role: 'system',
              content: `Error: ${error instanceof Error ? error.message : String(error)}`,
              format: 'plain'
            }]);
          }
        );
      } catch (error) {
        messageStore.update(messages =>
          messages.filter(m => m.format !== 'loading')
        );
        throw error;
      }
    } catch (error) {
      console.error('Chat submission error:', error);
      messageStore.update(messages =>
        messages.filter(m => m.format !== 'loading')
      );
      messageStore.update(messages => [...messages, {
        role: 'system',
        content: `Error: ${error instanceof Error ? error.message : String(error)}`,
        format: 'plain'
      }]);
    } finally {
      messageStore.update(messages =>
        messages.filter(m => m.format !== 'loading')
      );
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSubmit();
    }
  }
</script>

<div class="flex flex-col p-2">
  <div class="relative bg-primary-800/30 rounded-lg">
    <Textarea
      bind:value={userInput}
      oninput={handleInput}
      onkeydown={handleKeydown}
      placeholder="Message... (paste YouTube URLs to process)"
      class="w-full resize-none bg-transparent border-none text-sm focus:ring-1 focus:ring-white/20 transition-colors p-3 pr-24 min-h-[44px] max-h-[200px] overflow-y-auto"
      rows={2}
    />
    <div class="absolute bottom-2 right-2 z-10 flex items-center gap-1.5">
      {#if isFileIndicatorVisible}
        <span class="text-xs text-white/70">
          {uploadedFiles.length} file{uploadedFiles.length > 1 ? 's' : ''}
        </span>
      {/if}
      {#key fileButtonKey}
        <FileButton
          name="file-upload"
          button="btn-icon variant-ghost"
          bind:files
          on:change={handleFileUpload}
          disabled={isProcessingFiles || uploadedFiles.length >= 5}
          class="h-8 w-8 bg-primary-800/30 hover:bg-primary-800/50 rounded-full transition-colors"
        >
          <Paperclip class="w-4 h-4" />
        </FileButton>
      {/key}
      <Button
        type="button"
        variant="ghost"
        size="icon"
        name="send"
        onclick={handleSubmit}
        disabled={isProcessingFiles || !userInput.trim()}
        class="h-8 w-8 bg-primary-800/30 hover:bg-primary-800/50 rounded-full transition-colors disabled:opacity-30"
      >
        <Send class="w-4 h-4" />
      </Button>
    </div>
  </div>
</div>

<style>
  :global(textarea) {
    scrollbar-width: thin;
    scrollbar-color: rgba(255, 255, 255, 0.2) transparent;
  }

  :global(textarea::-webkit-scrollbar) {
    width: 6px;
  }

  :global(textarea::-webkit-scrollbar-track) {
    background: transparent;
  }

  :global(textarea::-webkit-scrollbar-thumb) {
    background-color: rgba(255, 255, 255, 0.2);
    border-radius: 3px;
  }

  :global(textarea::-webkit-scrollbar-thumb:hover) {
    background-color: rgba(255, 255, 255, 0.3);
  }

  :global(textarea::selection) {
    background-color: rgba(255, 255, 255, 0.1);
  }
</style>
