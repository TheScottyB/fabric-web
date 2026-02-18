#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';

const cwd = process.cwd();
const envPath = path.join(cwd, '.env');

const fileVars = {};
if (fs.existsSync(envPath)) {
  const lines = fs.readFileSync(envPath, 'utf8').split(/\r?\n/);
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#') || !trimmed.includes('=')) continue;
    const idx = trimmed.indexOf('=');
    const key = trimmed.slice(0, idx).trim();
    const value = trimmed.slice(idx + 1).trim();
    fileVars[key] = value;
  }
}

const getVar = (key) => {
  const fromEnv = process.env[key];
  if (typeof fromEnv === 'string' && fromEnv.trim().length > 0) return fromEnv.trim();
  const fromFile = fileVars[key];
  return typeof fromFile === 'string' && fromFile.trim().length > 0 ? fromFile.trim() : '';
};

const requiredAlways = ['DEFAULT_VENDOR', 'DEFAULT_MODEL'];
const providerKeys = [
  'OPENAI_API_KEY',
  'ANTHROPIC_API_KEY',
  'GOOGLE_API_KEY',
  'AZURE_OPENAI_API_KEY',
  'GROQ_API_KEY',
  'DEEPSEEK_API_KEY'
];

const missingAlways = requiredAlways.filter((key) => getVar(key) === '');
if (missingAlways.length > 0) {
  console.error(`Missing required environment variables: ${missingAlways.join(', ')}`);
  process.exit(1);
}

const hasProviderKey = providerKeys.some((key) => getVar(key) !== '');
const hasOllamaBase = getVar('OLLAMA_API_BASE') !== '';
const skipProviderCheck = process.env.CI === 'true';

if (!skipProviderCheck && !hasProviderKey && !hasOllamaBase) {
  console.error(
    'No model provider configured. Set at least one provider API key or OLLAMA_API_BASE.'
  );
  process.exit(1);
}

console.log('Environment validation passed.');
