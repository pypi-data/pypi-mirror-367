<script lang="ts">
	import { marked } from 'marked';
	import { createEventDispatcher } from 'svelte';
	import type { SelectData } from '@gradio/utils';

	export let markdown_content: string = '';
	export let highlights: Array<{
		term?: string;
		position?: number[];
		title: string;
		content: string;
		category: string;
		color: string;
	}> = [];
	export let show_side_panel: boolean = true;
	export let panel_width: string = '300px';

	const dispatch = createEventDispatcher<{
		select: SelectData;
	}>();

	let selectedHighlight: typeof highlights[0] | null = null;
	let processedHtml: string = '';
	let panelContent: string = '';

	// Process markdown and apply highlighting
	$: {
		if (markdown_content) {
			processMarkdown();
		}
	}

	// Process panel content
	$: {
		if (selectedHighlight) {
			processPanelContent();
		}
	}

	async function processMarkdown() {
		// Separate position-based and term-based highlights
		const positionHighlights = highlights.filter(h => h.position && h.position.length === 2);
		const termHighlights = highlights.filter(h => h.term && h.term.trim());
		
		// Apply position-based highlights first by inserting special markers
		let processedMarkdown = applyPositionMarkers(markdown_content, positionHighlights);
		
		// Then parse the markdown to HTML
		let html = await marked(processedMarkdown);
		
		// Replace position markers with actual highlight spans
		html = replacePositionMarkers(html, positionHighlights);
		
		// Apply term-based highlights to the HTML
		termHighlights.forEach(highlight => {
			if (highlight.term && highlight.term.trim()) {
				const index = highlights.indexOf(highlight);
				const regex = new RegExp(`\\b${escapeRegex(highlight.term)}\\b`, 'gi');
				html = html.replace(regex, (match: string) => {
					const color = highlight.color || '#e3f2fd';
					return `<span class="highlight-term" 
								data-index="${index}" 
								data-term="${highlight.term}"
								style="background-color: ${color}; cursor: pointer; padding: 2px 4px; border-radius: 3px; transition: all 0.2s;"
								role="button" 
								tabindex="0" 
								aria-label="Highlighted term: ${highlight.term}">
							${match}
						</span>`;
				});
			}
		});
		
		processedHtml = html;
	}

	function applyPositionMarkers(content: string, positionHighlights: typeof highlights): string {
		// Sort highlights by start position in descending order to avoid position shifts
		const sortedHighlights = [...positionHighlights].sort((a, b) => (b.position![0] - a.position![0]));
		
		let result = content;
		
		sortedHighlights.forEach(highlight => {
			const [start, end] = highlight.position!;
			if (start >= 0 && end <= result.length && start < end) {
				const targetText = result.substring(start, end);
				const index = highlights.indexOf(highlight);
				
				// Skip if the highlight crosses structural markdown boundaries
				if (crossesMarkdownBoundary(targetText)) {
					console.warn(`Position highlight [${start}, ${end}] crosses markdown boundary, skipping`);
					return;
				}
				
				// Create unique markers that won't interfere with markdown rendering
				const startMarker = `|||POSHL_START_${index}|||`;
				const endMarker = `|||POSHL_END_${index}|||`;
				
				result = result.substring(0, start) + startMarker + targetText + endMarker + result.substring(end);
			}
		});
		
		return result;
	}

	function crossesMarkdownBoundary(text: string): boolean {
		// Check if the highlighted text crosses markdown structural boundaries
		// that would break the markdown parsing
		return (
			text.includes('\n#') ||           // Header boundaries
			text.includes('\n\n') ||         // Paragraph boundaries  
			text.includes('\n-') ||          // List boundaries
			text.includes('\n*') ||          // List boundaries
			text.includes('\n1.') ||         // Numbered list boundaries
			text.includes('\n>') ||          // Blockquote boundaries
			text.includes('\n```') ||        // Code block boundaries
			text.includes('\n|') ||          // Table boundaries
			!!text.match(/^\s*#/) ||         // Starts with header
			!!text.match(/\n\s*#/)          // Contains header start
		);
	}

	function replacePositionMarkers(html: string, positionHighlights: typeof highlights): string {
		positionHighlights.forEach(highlight => {
			const [start, end] = highlight.position!;
			if (start >= 0 && end <= markdown_content.length && start < end) {
				const targetText = markdown_content.substring(start, end);
				const color = highlight.color || '#e3f2fd';
				const index = highlights.indexOf(highlight);
				
				const startMarker = `|||POSHL_START_${index}|||`;
				const endMarker = `|||POSHL_END_${index}|||`;
				
				// Find and replace the markers with highlight spans
				const markerRegex = new RegExp(`\\|\\|\\|POSHL_START_${index}\\|\\|\\|(.*?)\\|\\|\\|POSHL_END_${index}\\|\\|\\|`, 'g');
				
				html = html.replace(markerRegex, (match, content) => {
					return `<span class="highlight-position" 
						data-index="${index}" 
						data-text="${encodeURIComponent(targetText)}"
						style="background-color: ${color}; cursor: pointer; padding: 2px 4px; border-radius: 3px; transition: all 0.2s;"
						role="button" 
						tabindex="0" 
						aria-label="Highlighted text: ${targetText.replace(/"/g, '&quot;')}">
						${content}
					</span>`;
				});
			}
		});
		
		return html;
	}

	async function processPanelContent() {
		if (selectedHighlight) {
			panelContent = await marked(selectedHighlight.content || 'No additional information available.');
		}
	}

	function escapeRegex(string: string): string {
		return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
	}

	function handleTermClick(event: Event) {
		const target = event.target as HTMLElement;
		if (target.classList.contains('highlight-term') || target.classList.contains('highlight-position')) {
			const index = parseInt(target.dataset.index || '0');
			const highlight = highlights[index];
			if (highlight) {
				selectedHighlight = highlight;
				dispatch('select', {
					index,
					value: highlight
				});
			}
		}
	}

	function handleKeydown(event: KeyboardEvent) {
		const target = event.target as HTMLElement;
		if ((event.key === 'Enter' || event.key === ' ') && 
			(target.classList.contains('highlight-term') || target.classList.contains('highlight-position'))) {
			event.preventDefault();
			handleTermClick(event);
		}
	}

	function closeSidePanel() {
		selectedHighlight = null;
	}
</script>

<div class="markdown-container" class:with-panel={show_side_panel && selectedHighlight}>
	<div class="markdown-content" on:click={handleTermClick} on:keydown={handleKeydown} role="document" aria-label="Markdown content with interactive highlights">
		{@html processedHtml}
	</div>
	
	{#if show_side_panel && selectedHighlight}
		<div class="side-panel" style="width: {panel_width}">
			<div class="panel-header">
				<h3>{selectedHighlight.title || selectedHighlight.term || 'Highlighted Text'}</h3>
				<button class="close-btn" on:click={closeSidePanel}>×</button>
			</div>
			<div class="panel-content">
				{#if selectedHighlight.category}
					<div class="category-badge" style="background-color: {selectedHighlight.color || '#e3f2fd'}">
						{selectedHighlight.category}
					</div>
				{/if}
				<div class="content-text">
					{@html panelContent}
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	.markdown-container {
		display: flex;
		height: 100%;
		position: relative;
		transition: all 0.3s ease;
	}

	.markdown-content {
		flex: 1;
		padding: var(--block-padding);
		overflow-y: auto;
		transition: margin-right 0.3s ease;
	}

	.with-panel .markdown-content {
		margin-right: var(--spacing-md);
	}

	.side-panel {
		position: fixed;
		top: 0;
		right: 0;
		height: 100vh;
		background: var(--background-fill-primary);
		border-left: 1px solid var(--border-color-primary);
		box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
		z-index: 1000;
		overflow-y: auto;
		transform: translateX(0);
		transition: transform 0.3s ease;
	}

	.panel-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: var(--size-4);
		border-bottom: 1px solid var(--border-color-primary);
		background: var(--background-fill-secondary);
	}

	.panel-header h3 {
		margin: 0;
		font-size: var(--text-lg);
		font-weight: var(--weight-semibold);
		color: var(--body-text-color);
	}

	.close-btn {
		background: none;
		border: none;
		font-size: var(--text-xl);
		cursor: pointer;
		color: var(--body-text-color);
		padding: var(--size-1);
		border-radius: var(--radius-sm);
		transition: background-color 0.2s;
	}

	.close-btn:hover {
		background-color: var(--background-fill-primary);
	}

	.panel-content {
		padding: var(--size-4);
	}

	.category-badge {
		display: inline-block;
		padding: var(--size-1) var(--size-2);
		border-radius: var(--radius-full);
		font-size: var(--text-sm);
		font-weight: var(--weight-medium);
		margin-bottom: var(--size-3);
		color: var(--body-text-color);
	}

	.content-text {
		line-height: 1.6;
		color: var(--body-text-color);
	}

	/* Markdown styling */
	.markdown-content :global(h1) {
		font-size: var(--text-2xl);
		font-weight: var(--weight-bold);
		margin: var(--size-4) 0 var(--size-2) 0;
		color: var(--body-text-color);
	}

	.markdown-content :global(h2) {
		font-size: var(--text-xl);
		font-weight: var(--weight-semibold);
		margin: var(--size-3) 0 var(--size-2) 0;
		color: var(--body-text-color);
	}

	.markdown-content :global(h3) {
		font-size: var(--text-lg);
		font-weight: var(--weight-medium);
		margin: var(--size-3) 0 var(--size-1) 0;
		color: var(--body-text-color);
	}

	.markdown-content :global(p) {
		margin: var(--size-2) 0;
		line-height: 1.6;
		color: var(--body-text-color);
	}

	.markdown-content :global(strong) {
		font-weight: var(--weight-bold);
	}

	.markdown-content :global(em) {
		font-style: italic;
	}

	.markdown-content :global(ul), .markdown-content :global(ol) {
		margin: var(--size-2) 0;
		padding-left: var(--size-4);
		color: var(--body-text-color);
	}

	.markdown-content :global(li) {
		margin: var(--size-1) 0;
	}

	.markdown-content :global(code) {
		background-color: var(--background-fill-secondary);
		padding: var(--size-1);
		border-radius: var(--radius-sm);
		font-family: var(--font-mono);
		font-size: var(--text-sm);
	}

	.markdown-content :global(pre) {
		background-color: var(--background-fill-secondary);
		padding: var(--size-3);
		border-radius: var(--radius-md);
		overflow-x: auto;
		margin: var(--size-2) 0;
	}

	.markdown-content :global(pre code) {
		background: none;
		padding: 0;
	}

	.markdown-content :global(.highlight-term:hover),
	.markdown-content :global(.highlight-position:hover),
	.markdown-content :global(.highlight-term:focus),
	.markdown-content :global(.highlight-position:focus) {
		opacity: 0.8;
		transform: scale(1.02);
		outline: 2px solid var(--color-accent);
		outline-offset: 1px;
	}

	/* Responsive design */
	@media (max-width: 768px) {
		.side-panel {
			width: 100% !important;
		}
		
		.with-panel .markdown-content {
			margin-right: 0;
		}
	}
</style>