import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { YoutubeTranscript } from 'youtube-transcript';

const FABRIC_BASE_URL = (
  process.env.FABRIC_API_URL ||
  process.env.FABRIC_BASE_URL ||
  'http://localhost:8080'
).replace(/\/+$/, '');

type JsonRecord = Record<string, unknown>;

interface PromptRequest {
  userInput?: string;
  patternName?: string;
  strategyName?: string;
  sessionName?: string;
  contextName?: string;
  model?: string;
  vendor?: string;
  variables?: Record<string, string>;
}

interface ChatRequestPayload {
  prompts: PromptRequest[];
  language?: string;
  temperature?: number;
  topP?: number;
  frequencyPenalty?: number;
  presencePenalty?: number;
  [key: string]: unknown;
}

const passthroughKeys = [
  'messages',
  'model',
  'maxTokens',
  'modelContextLength',
  'raw',
  'search',
  'searchLocation',
  'seed',
  'quiet',
  'thinking',
  'thinkStartTag',
  'thinkEndTag',
  'suppressThink',
  'notification',
  'notificationCommand',
  'showMetadata',
  'audioOutput',
  'audioFormat',
  'voice',
  'imageFile',
  'imageSize',
  'imageQuality',
  'imageBackground',
  'imageCompression'
] as const;

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === 'object' && value !== null;
}

function asString(value: unknown): string | undefined {
  return typeof value === 'string' && value.trim().length > 0
    ? value.trim()
    : undefined;
}

function asNumber(value: unknown): number | undefined {
  return typeof value === 'number' && Number.isFinite(value) ? value : undefined;
}

function toVariables(value: unknown): Record<string, string> | undefined {
  if (!isRecord(value)) return undefined;

  const entries = Object.entries(value).filter(([, v]) => typeof v === 'string');
  if (entries.length === 0) return undefined;

  return Object.fromEntries(entries) as Record<string, string>;
}

function normalizePrompt(prompt: JsonRecord, fallback: JsonRecord): PromptRequest {
  return {
    userInput: asString(prompt.userInput) ?? asString(fallback.input),
    patternName: asString(prompt.patternName) ?? asString(fallback.pattern),
    strategyName: asString(prompt.strategyName) ?? asString(fallback.strategy),
    sessionName: asString(prompt.sessionName) ?? asString(fallback.sessionName),
    contextName: asString(prompt.contextName),
    model: asString(prompt.model) ?? asString(fallback.model),
    vendor: asString(prompt.vendor),
    variables: toVariables(prompt.variables) ?? toVariables(fallback.variables)
  };
}

function normalizeChatPayload(rawBody: JsonRecord): ChatRequestPayload {
  const promptsFromRequest = Array.isArray(rawBody.prompts)
    ? rawBody.prompts
        .filter(isRecord)
        .map((prompt) => normalizePrompt(prompt, rawBody))
        .filter((prompt) => prompt.userInput || prompt.patternName)
    : [];

  const prompts =
    promptsFromRequest.length > 0
      ? promptsFromRequest
      : [normalizePrompt({}, rawBody)].filter(
          (prompt) => prompt.userInput || prompt.patternName
        );

  const payload: ChatRequestPayload = { prompts };

  const language = asString(rawBody.language);
  if (language) payload.language = language;

  const temperature = asNumber(rawBody.temperature);
  if (temperature !== undefined) payload.temperature = temperature;

  const topP = asNumber(rawBody.topP) ?? asNumber(rawBody.top_p);
  if (topP !== undefined) payload.topP = topP;

  const frequencyPenalty =
    asNumber(rawBody.frequencyPenalty) ?? asNumber(rawBody.frequency_penalty);
  if (frequencyPenalty !== undefined) payload.frequencyPenalty = frequencyPenalty;

  const presencePenalty =
    asNumber(rawBody.presencePenalty) ?? asNumber(rawBody.presence_penalty);
  if (presencePenalty !== undefined) payload.presencePenalty = presencePenalty;

  for (const key of passthroughKeys) {
    if (rawBody[key] !== undefined) {
      payload[key] = rawBody[key];
    }
  }

  return payload;
}

async function sendToFabricChat(payload: ChatRequestPayload): Promise<Response> {
  const endpoints = ['/chat', '/api/chat'];
  let lastResponse: Response | null = null;
  let lastError: Error | null = null;

  for (const endpoint of endpoints) {
    try {
      const response = await fetch(`${FABRIC_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (response.status === 404) {
        lastResponse = response;
        continue;
      }

      return response;
    } catch (error) {
      lastError =
        error instanceof Error
          ? error
          : new Error(`Failed to call Fabric endpoint ${endpoint}`);
    }
  }

  if (lastResponse) return lastResponse;
  if (lastError) throw lastError;

  throw new Error('Unable to reach Fabric chat endpoint');
}

export const POST: RequestHandler = async ({ request }) => {
  try {
    const rawBody = await request.json();
    if (!isRecord(rawBody)) {
      return json({ error: 'Invalid JSON request body' }, { status: 400 });
    }
    console.log('\n=== Request Analysis ===');
    console.log('1. Raw request body:', JSON.stringify(rawBody, null, 2));

    // Handle YouTube URL request
    if (rawBody.url) {
      const url = asString(rawBody.url);
      const language = asString(rawBody.language);
      if (!url) {
        return json({ error: 'Invalid YouTube URL' }, { status: 400 });
      }

      console.log('2. Processing YouTube URL:', {
        url,
        language,
        hasLanguageParam: true
      });

      // Extract video ID
      const match = url.match(/(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/);
      const videoId = match ? match[1] : null;

      if (!videoId) {
        return json({ error: 'Invalid YouTube URL' }, { status: 400 });
      }

      console.log('3. Video ID:', {
        id: videoId,
        language
      });

      const transcriptItems = await YoutubeTranscript.fetchTranscript(videoId);
      const transcript = transcriptItems
        .map(item => item.text)
        .join(' ');

      // Create response with transcript and language
      const response = {
        transcript,
        title: videoId,
        language
      };

      console.log('4. Transcript processed:', {
        length: transcript.length,
        language,
        firstChars: transcript.substring(0, 50),
        responseSize: JSON.stringify(response).length
      });

      return json(response);
    }

    const payload = normalizeChatPayload(rawBody);
    const [firstPrompt] = payload.prompts;
    if (!firstPrompt?.userInput && !firstPrompt?.patternName) {
      return json(
        {
          error:
            "Invalid chat request. Provide either prompts[] or legacy fields 'input' and 'pattern'."
        },
        { status: 400 }
      );
    }

    // Handle pattern execution request
    console.log('\n=== Server Request Analysis ===');
    console.log('1. Request overview:', {
      pattern: firstPrompt?.patternName,
      hasPrompts: !!payload.prompts?.length,
      messageCount: Array.isArray(payload.messages) ? payload.messages.length : 0,
      isYouTube: 'No',
      language: payload.language
    });

    console.log('2. Language analysis:', {
      input: firstPrompt?.userInput?.substring(0, 100),
      hasLanguageInstruction: firstPrompt?.userInput?.includes('language'),
      containsFr: firstPrompt?.userInput?.includes('fr'),
      containsEn: firstPrompt?.userInput?.includes('en'),
      requestLanguage: payload.language
    });

    // Log full request for debugging
    console.log('3. Normalized request:', JSON.stringify(payload, null, 2));

    // Log important fields
    console.log('4. Key fields:', {
      patternName: firstPrompt?.patternName,
      inputLength: firstPrompt?.userInput?.length,
      messageCount: Array.isArray(payload.messages) ? payload.messages.length : 0
    });

    console.log('5. Sending to Fabric backend...');
    const fabricResponse = await sendToFabricChat(payload);

    console.log('6. Fabric response:', {
      status: fabricResponse.status,
      ok: fabricResponse.ok,
      statusText: fabricResponse.statusText
    });

    if (!fabricResponse.ok) {
      const responseBody = await fabricResponse.text();
      console.error('Error from Fabric API:', {
        status: fabricResponse.status,
        statusText: fabricResponse.statusText,
        body: responseBody
      });
      throw new Error(
        `Fabric API error: ${fabricResponse.status} ${fabricResponse.statusText}${responseBody ? ` - ${responseBody}` : ''}`
      );
    }

    const stream = fabricResponse.body;
    if (!stream) {
      throw new Error('No response from fabric backend');
    }

    const responseHeaders = new Headers();
    responseHeaders.set(
      'Content-Type',
      fabricResponse.headers.get('Content-Type') || 'text/event-stream'
    );
    responseHeaders.set('Cache-Control', 'no-cache');
    responseHeaders.set('Connection', 'keep-alive');

    // Return the stream to the browser
    return new Response(stream, {
      headers: {
        ...Object.fromEntries(responseHeaders.entries())
      }
    });

  } catch (error) {
    console.error('\n=== Error ===');
    console.error('Type:', error?.constructor?.name);
    console.error('Message:', error instanceof Error ? error.message : String(error));
    console.error('Stack:', error instanceof Error ? error.stack : 'No stack trace');
    return json(
      { error: error instanceof Error ? error.message : 'Failed to process request' },
      { status: 500 }
    );
  }
};
