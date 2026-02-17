
// this file is generated — do not edit it


declare module "svelte/elements" {
	export interface HTMLAttributes<T> {
		'data-sveltekit-keepfocus'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-noscroll'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-preload-code'?:
			| true
			| ''
			| 'eager'
			| 'viewport'
			| 'hover'
			| 'tap'
			| 'off'
			| undefined
			| null;
		'data-sveltekit-preload-data'?: true | '' | 'hover' | 'tap' | 'off' | undefined | null;
		'data-sveltekit-reload'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-replacestate'?: true | '' | 'off' | undefined | null;
	}
}

export {};


declare module "$app/types" {
	export interface AppTypes {
		RouteId(): "/" | "/about" | "/api" | "/api/youtube" | "/api/youtube/transcript" | "/chat" | "/contact" | "/notes" | "/obsidian" | "/posts" | "/posts/[slug]" | "/tags" | "/tags/[tag]";
		RouteParams(): {
			"/posts/[slug]": { slug: string };
			"/tags/[tag]": { tag: string }
		};
		LayoutParams(): {
			"/": { slug?: string; tag?: string };
			"/about": Record<string, never>;
			"/api": Record<string, never>;
			"/api/youtube": Record<string, never>;
			"/api/youtube/transcript": Record<string, never>;
			"/chat": Record<string, never>;
			"/contact": Record<string, never>;
			"/notes": Record<string, never>;
			"/obsidian": Record<string, never>;
			"/posts": { slug?: string };
			"/posts/[slug]": { slug: string };
			"/tags": { tag?: string };
			"/tags/[tag]": { tag: string }
		};
		Pathname(): "/" | "/about" | "/about/" | "/api" | "/api/" | "/api/youtube" | "/api/youtube/" | "/api/youtube/transcript" | "/api/youtube/transcript/" | "/chat" | "/chat/" | "/contact" | "/contact/" | "/notes" | "/notes/" | "/obsidian" | "/obsidian/" | "/posts" | "/posts/" | `/posts/${string}` & {} | `/posts/${string}/` & {} | "/tags" | "/tags/" | `/tags/${string}` & {} | `/tags/${string}/` & {};
		ResolvedPathname(): `${"" | `/${string}`}${ReturnType<AppTypes['Pathname']>}`;
		Asset(): "/brain.png" | "/data/pattern_descriptions.json" | "/electric.png" | "/fabric-logo.gif" | "/fabric-logo.png" | "/fabric-summarize.png" | "/favicon.png" | "/obsidian-logo.png" | "/robots.txt" | "/strategies/strategies.json" | string & {};
	}
}