import adapter from '@sveltejs/adapter-node';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
import { mdsvex } from 'mdsvex';
import rehypeSlug from 'rehype-slug';
import rehypeAutolinkHeadings from 'rehype-autolink-headings';
import rehypeExternalLinks from 'rehype-external-links';
import rehypeUnwrapImages from 'rehype-unwrap-images';
import { escapeSvelte } from 'mdsvex';
import { getSingletonHighlighter } from 'shiki';
import dracula from 'shiki/themes/dracula.mjs';

const initializeHighlighter = async () => {
  try {
    return await getSingletonHighlighter({
      themes: ['dracula'],
      langs: [
        'javascript',
        'typescript',
        'svelte',
        'markdown',
        'bash',
        'go',
        'text',
        'python',
        'rust',
        'c',
        'c++',
        'shell',
        'powershell',
        'ruby',
        'json',
        'html',
        'css',
        'java',
        'sql',
        'toml',
        'yaml'
      ]
    });
  } catch (error) {
    console.error('Failed to initialize Shiki highlighter:', error);
    return null;
  }
};

const shikiHighlighterPromise = initializeHighlighter();

/** @type {import('mdsvex').MdsvexOptions} */
const mdsvexOptions = {
  extensions: ['.md', '.svx'],
  smartypants: {
    quotes: true,
    ellipses: true,
    backticks: true,
    dashes: true
  },
  highlight: {
    highlighter: async (code, lang) => {
      try {
        const highlighter = await shikiHighlighterPromise;
        if (!highlighter) {
          console.warn('Shiki highlighter not available, falling back to plain text');
          return `<pre><code>${escapeSvelte(code)}</code></pre>`;
        }

        const requestedLang = typeof lang === 'string' ? lang.toLowerCase() : 'text';
        const loadedLangs = new Set(
          (highlighter.getLoadedLanguages?.() || []).map((value) => String(value).toLowerCase())
        );
        const safeLang = loadedLangs.has(requestedLang) ? requestedLang : 'text';
        const html = escapeSvelte(highlighter.codeToHtml(code, { lang: safeLang, theme: dracula }));
        return `{@html \`${html}\`}`;
      } catch (error) {
        console.error('Failed to highlight code:', error);
        return `<pre><code>${escapeSvelte(code)}</code></pre>`;
      }
    }
  },
  rehypePlugins: [
    rehypeSlug,
    rehypeUnwrapImages,
    [rehypeAutolinkHeadings, { behavior: 'wrap' }],
    [rehypeExternalLinks, { target: '_blank', rel: ['nofollow', 'noopener', 'noreferrer'] }]
  ]
};

/** @type {import('@sveltejs/kit').Config} */
const config = {
  extensions: ['.svelte', '.md', '.svx'],
  kit: {
    adapter: adapter(),
    prerender: {
      handleHttpError: ({ path, referrer, message }) => {
        console.warn(`HTTP error during prerendering: ${message}\nPath: ${path}\nReferrer: ${referrer}`);

        if (path === '/not-found' && referrer === '/') {
          return;
        }

        throw new Error(message);
      }
    }
  },
  preprocess: [
    vitePreprocess({
      script: true
    }),
    mdsvex(mdsvexOptions)
  ]
};

export default config;
