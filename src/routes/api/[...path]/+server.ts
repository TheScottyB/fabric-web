import { env } from '$env/dynamic/private';
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const FABRIC_BASE_URL = (
  env.FABRIC_API_URL ||
  env.FABRIC_BASE_URL ||
  'http://localhost:8080'
).replace(/\/+$/, '');

/**
 * Catch-all proxy that forwards /api/* requests to the Fabric backend,
 * stripping the /api prefix. This mirrors the Vite dev server proxy
 * so the same fetch calls work in both dev and production.
 *
 * More specific routes (e.g. /api/youtube/transcript) take priority
 * over this catch-all in SvelteKit's routing.
 */
async function proxyRequest(request: Request, path: string): Promise<Response> {
  const url = new URL(request.url);
  const targetUrl = `${FABRIC_BASE_URL}/${path}${url.search}`;

  try {
    const headers = new Headers(request.headers);
    headers.delete('host');

    const init: RequestInit = {
      method: request.method,
      headers,
    };

    if (request.method !== 'GET' && request.method !== 'HEAD') {
      init.body = await request.arrayBuffer();
    }

    const response = await fetch(targetUrl, init);

    if (!response.ok && response.status !== 404) {
      console.error(`[api-proxy] ${request.method} /${path} → ${response.status} ${response.statusText}`);
    }

    return response;
  } catch (error) {
    console.error(`[api-proxy] ${request.method} /${path} → connection failed:`, error instanceof Error ? error.message : error);
    return json(
      { error: 'Fabric backend unavailable' },
      { status: 502 }
    );
  }
}

export const GET: RequestHandler = async ({ request, params }) => {
  return proxyRequest(request, params.path);
};

export const POST: RequestHandler = async ({ request, params }) => {
  return proxyRequest(request, params.path);
};

export const PUT: RequestHandler = async ({ request, params }) => {
  return proxyRequest(request, params.path);
};

export const DELETE: RequestHandler = async ({ request, params }) => {
  return proxyRequest(request, params.path);
};

export const PATCH: RequestHandler = async ({ request, params }) => {
  return proxyRequest(request, params.path);
};
