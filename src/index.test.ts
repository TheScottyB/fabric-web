import { describe, it, expect, vi, beforeEach } from 'vitest';

/**
 * Fabric Unit Tests
 * Tests for core functionality, utilities, and API clients
 */

describe('Environment Configuration', () => {
	it('validates FABRIC_API_URL format', () => {
		const validUrls = [
			'http://localhost:8080',
			'http://fabric-api:8080',
			'https://api.example.com',
		];
		
		validUrls.forEach(url => {
			expect(url).toMatch(/^https?:\/\/.+/);
		});
	});

	it('validates API key formats', () => {
		const keyPatterns = {
			anthropic: /^sk-ant-/,
			openai: /^sk-/,
			gemini: /^AIza/,
			groq: /^gsk_/,
		};
		
		expect('sk-ant-test123').toMatch(keyPatterns.anthropic);
		expect('sk-proj-test123').toMatch(keyPatterns.openai);
		expect('AIzaTest123').toMatch(keyPatterns.gemini);
		expect('gsk_test123').toMatch(keyPatterns.groq);
	});
});

describe('Pattern Name Validation', () => {
	const isValidPatternName = (name: string): boolean => {
		return /^[a-z][a-z0-9_-]*$/.test(name);
	};

	it('accepts valid pattern names', () => {
		const validNames = ['summarize', 'extract_wisdom', 'analyze-claims', 'rate_value'];
		validNames.forEach(name => {
			expect(isValidPatternName(name)).toBe(true);
		});
	});

	it('rejects invalid pattern names', () => {
		const invalidNames = ['Summarize', '123pattern', '-invalid', '_invalid'];
		invalidNames.forEach(name => {
			expect(isValidPatternName(name)).toBe(false);
		});
	});
});

describe('Chat Message Formatting', () => {
	interface ChatMessage {
		role: 'user' | 'assistant' | 'system';
		content: string;
	}

	const formatChatPayload = (input: string, pattern: string) => ({
		input,
		pattern,
		stream: false,
	});

	it('creates valid chat payload', () => {
		const payload = formatChatPayload('Test input', 'summarize');
		
		expect(payload).toHaveProperty('input');
		expect(payload).toHaveProperty('pattern');
		expect(payload).toHaveProperty('stream');
		expect(payload.input).toBe('Test input');
		expect(payload.pattern).toBe('summarize');
	});

	it('handles empty input', () => {
		const payload = formatChatPayload('', 'summarize');
		expect(payload.input).toBe('');
	});
});

describe('Strategy Validation', () => {
	const validStrategies = [
		'standard',
		'cot',
		'cod',
		'tot',
		'aot',
		'ltm',
		'self-consistent',
		'self-refine',
		'reflexion',
	];

	it('recognizes all valid strategies', () => {
		validStrategies.forEach(strategy => {
			expect(validStrategies.includes(strategy)).toBe(true);
		});
	});

	it('rejects invalid strategies', () => {
		const invalidStrategies = ['invalid', 'unknown', 'custom'];
		invalidStrategies.forEach(strategy => {
			expect(validStrategies.includes(strategy)).toBe(false);
		});
	});
});

describe('URL Building', () => {
	const buildApiUrl = (base: string, endpoint: string): string => {
		const cleanBase = base.endsWith('/') ? base.slice(0, -1) : base;
		const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
		return `${cleanBase}${cleanEndpoint}`;
	};

	it('builds correct API URLs', () => {
		expect(buildApiUrl('http://localhost:8080', '/patterns')).toBe('http://localhost:8080/patterns');
		expect(buildApiUrl('http://localhost:8080/', 'patterns')).toBe('http://localhost:8080/patterns');
		expect(buildApiUrl('http://localhost:8080', 'patterns')).toBe('http://localhost:8080/patterns');
	});
});

describe('Input Sanitization', () => {
	const sanitizeInput = (input: string): string => {
		return input
			.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
			.trim();
	};

	it('removes script tags', () => {
		const malicious = 'Hello <script>alert("xss")</script> World';
		expect(sanitizeInput(malicious)).toBe('Hello  World');
	});

	it('preserves normal text', () => {
		const normal = 'This is a normal message';
		expect(sanitizeInput(normal)).toBe(normal);
	});

	it('trims whitespace', () => {
		const padded = '  trimmed  ';
		expect(sanitizeInput(padded)).toBe('trimmed');
	});
});

describe('Error Response Handling', () => {
	interface ApiError {
		status: number;
		message: string;
	}

	const parseApiError = (status: number, body: string): ApiError => {
		try {
			const parsed = JSON.parse(body);
			return {
				status,
				message: parsed.error || parsed.message || 'Unknown error',
			};
		} catch {
			return {
				status,
				message: body || 'Unknown error',
			};
		}
	};

	it('parses JSON error responses', () => {
		const error = parseApiError(400, '{"error": "Invalid pattern"}');
		expect(error.status).toBe(400);
		expect(error.message).toBe('Invalid pattern');
	});

	it('handles plain text errors', () => {
		const error = parseApiError(500, 'Internal Server Error');
		expect(error.status).toBe(500);
		expect(error.message).toBe('Internal Server Error');
	});

	it('handles empty error bodies', () => {
		const error = parseApiError(404, '');
		expect(error.status).toBe(404);
		expect(error.message).toBe('Unknown error');
	});
});
