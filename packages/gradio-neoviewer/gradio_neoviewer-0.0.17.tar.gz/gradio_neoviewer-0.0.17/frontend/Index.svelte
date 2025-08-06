<svelte:options accessors={true} />

<script lang="ts">
	import type { Gradio } from "@gradio/utils";
	import { tick, onMount } from 'svelte';
	import { FileData } from "@gradio/client";
	import { Block } from "@gradio/atoms";
	import { MarkdownCode } from "@gradio/markdown-code";
	import { StatusTracker } from "@gradio/statustracker";
	import type { LoadingStatus } from "@gradio/statustracker";

	export let elem_id = "";
	export let elem_classes: string[] = [];
	export let visible = true;
	export let value: null | FileData | FileData[];
	export let index_of_file_to_show: number;
	export let libre_office: boolean;
	export let max_size: number;
	export let max_pages: number;

	export let root: string;
	export let height: string | undefined;

	export let loading_status: LoadingStatus;
	export let container = true;
	export let scale: number | null = null;
	export let min_width: number | undefined = undefined;
	export let gradio: Gradio<{
		change: never;
		error: string;
		clear_status: LoadingStatus;
	}>;

	let pdfjsLib: any = null; // pour l'import dynamique de pdfjs
	let file: FileData;
	let old_file: null | FileData = null;

	let abortController = new AbortController();
	let blinking: HTMLDivElement;
	let viewer: HTMLDivElement;
	let shouldCancelImage = true;
	let shouldCancelMarkdown = true;
	let shouldCancelHtml = true;
	let shouldCancelPdf = true;

	let previous_file_title:string;
	let next_file_title: string;
	let download_title: string;

	// Variables pour le menu contextuel


	let showContextMenu: boolean = false;
    let menuX: number = 0;
    let menuY: number = 0;

	if (navigator.language.startsWith('fr')) {
		previous_file_title = "Fichier précédent";
		next_file_title = "Fichier suivant";
		download_title = "Télécharger le fichier";
	} else {
		previous_file_title = "Previous file";
		next_file_title = "Next file";
		download_title = "Download file";
	}
	
	
    function handleContextMenu(e: MouseEvent) {
		// show the context menu (only download link for now) on right click
		console.log("Context menu triggered");
		console.log("File to download:", file);
		if (!file) return;          // no file to download
		e.preventDefault();         // prevent the default context menu
		let absX = e.clientX;           // get the absolute position of the mouse
		let absY = e.clientY;
		// if the event comes from an iframe, we need to adjust the position from the iframe
		const iframe = viewer.querySelector('iframe'); // get the iframe if it exists
		if (iframe && iframe.contentDocument === e.view?.document) {
			const iframeRect = iframe.getBoundingClientRect();
			absX += iframeRect.left;
			absY += iframeRect.top;
		}
		// otherwise, we only ajust the position relative to the viewer (which can move depending on the size of the window)
		const rect = viewer.getBoundingClientRect();   // get the bounding rectangle of the viewer
		menuX = absX - rect.left;           // position relative to the viewer
		menuY = absY - rect.top;
		showContextMenu = true;
		console.log("Context menu position:", menuX, menuY);
		console.log("Context menu visibility:", showContextMenu);
    }

	function download(href: string, name: string) {
		// download utility function
		const a = document.createElement('a');
		a.href     = href;
		a.download = name;
		document.body.appendChild(a);
		a.click();
		a.remove();
	}

	async function downloadFile() {
		// download the file "file" when the context menu is clicked
		if (!file) return; // nothing to download
		try {
			if (imageFormats.some(ext => file.path.endsWith(ext))) {
				// For images, we need to fetch the binary data, otherwise the download will not work in some browsers
				// fetch the binary data
				const resp = await fetch(file.url);
				if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
				const buffer = await resp.arrayBuffer();
				// create a local blob URL
				const blob = new Blob([buffer], {
					type: resp.headers.get('Content-Type')
				});
				const blobUrl = URL.createObjectURL(blob);
				// trigger the download
				download(blobUrl, file.orig_name);
				// free the memory
				URL.revokeObjectURL(blobUrl);
			} else {
				// For other files, we can directly use the URL
				// we ensure we download the original file and not the pdf version
				const urlObj = new URL(file.url);
				const parts  = urlObj.pathname.split('/');
				parts[parts.length - 1] = encodeURIComponent(file.orig_name);
				urlObj.pathname = parts.join('/');
				download(urlObj.toString(), file.orig_name);
			}
		} catch (err) {
			console.error('Download failed:', err);
		} finally {
			showContextMenu = false;
		}
	}
			
		// function to close the context menu when clicking outside of it
		onMount(() => {
			const close = () => (showContextMenu = false);
			window.addEventListener('click', close);
			return () => window.removeEventListener('click', close);
		});


	function file_to_show(value: FileData | FileData[], index_of_file_to_show: number) {
		// function to get the file to show based on the value and index
		let file: null | FileData;
		if (Array.isArray(value) && value.length > 0) {
			file = value[index_of_file_to_show];
			} else if (value instanceof FileData) {
			file = value;
		}
		return file;
	}

	function addUrl(file: FileData, root: string) {
			if (file) {
				file.url = root + "/gradio_api/file=" + file.path
			}
			return file
		}

	$: if (value && (!Array.isArray(value) || value.length > 0) && visible) {
		// on n'affiche les fichiers que si value est défini et que le composant est visible
		// console.log("Value changed");
		if (value && JSON.stringify(file_to_show(value, index_of_file_to_show)) !== JSON.stringify(old_file)) {
			abortController.abort();
			shouldCancelHtml = true;
			shouldCancelImage = true;
			shouldCancelMarkdown = true;
			shouldCancelPdf = true;
			gradio.dispatch("change");
			old_file = file_to_show(value, index_of_file_to_show);
			file = addUrl(file_to_show(value, index_of_file_to_show), root);
			console.log(file.url);
			if (file.size > max_size) {
				console.log("Fichier trop lourd");
				showError('size');
			} else	if (file.path.endsWith('pdf') || libre_office && msFormats.some(ext => file.path.endsWith(ext))) {
				console.log("PDF ou MS");
				showPdf(file);
			} else if (htmlFormats.some(ext => file.path.endsWith(ext))) {
				console.log("HTML");
				if (file.size > max_size) {
					console.log("HTML trop lourd");
					showError('size');
				} else {
					showHtml(file);
				}
			} else if (imageFormats.some(ext => file.path.endsWith(ext))) {
				console.log("Image");
				showImage(file);
			} else if (markdownFormats.some(ext => file.path.endsWith(ext)) || codeFormats.some(ext => file.path.endsWith(ext))) {
				console.log("Markdown");
				if (file.size > max_size) {
					console.log("Markdown trop lourd");
					showError('size');
				} else {
					showMarkdown(file);
				}
			} else {
				console.log("Autre");
				showError('format');
			}
		}
	} else {
		showEmpty();
		old_file = null;
	}

	const htmlFormats = ['.html', '.svg'];
	const imageFormats = ['.png', '.jpg', '.jpeg'];
	const markdownFormats = ['.md', '.txt', '.csv', '.srt'];
	const msFormats = ['.docx', '.pptx', '.xlsx', '.doc', '.ppt', '.xls'];
	const codeFormats = ['.py', '.js', '.css', '.json', '.yaml', '.yml', '.xml', '.sh', '.bash', '.log', '.ts', '.tsx', '.js', '.jsx', '.cpp'];

	async function showEmpty() {
		abortController.abort();
		abortController = new AbortController();
		await tick();
		blinking.style.display = 'none';
		viewer.innerHTML = '';
	}

	async function showError(error: string) {
		console.log("Show error");
		abortController = new AbortController();
		await tick(); // Attend la fin du rendu
		blinking.style.display = 'none';
		let errorMessage: string;
		if (error == 'format') {
			errorMessage = navigator.language.startsWith('fr')
			? 'Format non pris en charge'
			: 'Unsupported format';
		} else if (error == 'size') {
			errorMessage = navigator.language.startsWith('fr')
			? 'Fichier trop volumineux pour être affiché'
			: 'File too heavy to be displayed';
		}
		viewer.innerHTML = `<div class="error-message">${errorMessage}</div>`;
	}

	function loadCSS(url) {
		return new Promise((resolve, reject) => {
			const link = document.createElement('link');
			link.rel = 'stylesheet';
			link.href = url;
			link.onload = () => resolve('Resource loaded successfully');
			link.onerror = () => reject(new Error(`Erreur lors du chargement du CSS : ${url}`));
			document.head.appendChild(link);
		});
	}


	async function showPdf(file: FileData) {
		if (!pdfjsLib) {
			pdfjsLib = await import('pdfjs-dist');
			pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
			await loadCSS('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf_viewer.min.css');
		}
		shouldCancelPdf = false;
		abortController = new AbortController();
		await tick(); // Attend la fin du rendu
		viewer.innerHTML = '';
		blinking.style.display = 'block';
		const loadingTask = pdfjsLib.getDocument(file.url);
		const pdfDoc = await loadingTask.promise;
		console.log('PDF loaded');

		if (pdfDoc.numPages > max_pages) {
			showError('size');
			return;
		}
		
		const fragment = document.createDocumentFragment(); // Crée un fragment de document

		const renderPage = async (pageNum: number) => {
			if (shouldCancelPdf) {
				console.log('Cancelled');
				return;
			}
			const page = await pdfDoc.getPage(pageNum);
			console.log(`Page ${pageNum} loaded`);
			const scale = 1.5;
			const viewport = page.getViewport({ scale: scale });

			// Création d'un conteneur pour la page (position relative)
			const pageContainer = document.createElement('div');
			pageContainer.className = 'pageContainer';
			pageContainer.style.position = 'relative';
			pageContainer.style.width = '100%';
			fragment.appendChild(pageContainer);

			// Création du canvas pour le rendu de la page
			const canvas = document.createElement('canvas');
			canvas.style.width = '100%';
			canvas.width = viewport.width;
			canvas.height = viewport.height;
			pageContainer.appendChild(canvas);

			const context = canvas.getContext('2d');

			// Rendu de la page dans le canvas
			const renderContext = { canvasContext: context, viewport };
			await page.render(renderContext).promise;
			console.log(`Page ${pageNum} rendered`);

			// Création de la couche de texte superposée
			const textLayerDiv = document.createElement('div');
			textLayerDiv.className = 'textLayer';
			textLayerDiv.style.position = 'absolute';
			textLayerDiv.style.top = '0';
			textLayerDiv.style.left = '0';
			textLayerDiv.style.width = canvas.width + 'px';
			textLayerDiv.style.height = canvas.height + 'px';
			pageContainer.appendChild(textLayerDiv);

			// Récupérer le contenu textuel de la page
			const textContent = await page.getTextContent();

			// Appel de renderTextLayer avec les bons arguments
			await pdfjsLib.renderTextLayer({
				textContentSource: textContent,
				container: textLayerDiv,         
				viewport: viewport,               
				textDivs: [],                     // tableau vide qui sera rempli par la fonction
				pageIndex: pageNum - 1,           // indice de la page (0-indexé)
				enhanceTextSelection: true        // améliore la sélection du texte
			});
};


		// Parallélisation du chargement et du rendu des pages
		const renderPromises = [];
		for (let pageNum = 1; pageNum <= pdfDoc.numPages; pageNum++) {
			if (shouldCancelPdf) {
				console.log('Cancelled');
				break;
			}
			renderPromises.push(renderPage(pageNum));
		}
		await Promise.all(renderPromises);
		if (!shouldCancelPdf) {
			viewer.appendChild(fragment); // Ajoute le fragment au conteneur
		} else {
			console.log('append viewer with pdf cancelled');
		}
		shouldCancelPdf = true;
		blinking.style.display = 'none';
	}

	async function showHtml(file: FileData) {
		shouldCancelHtml = false;
		abortController = new AbortController();
		await tick(); // Attend la fin du rendu
		viewer.innerHTML = ''; // Vide le conteneur
		blinking.style.display = 'block';
		try {
			const response = await fetch(file.url, {signal: abortController.signal});
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			const htmlContent = await response.text();

			const iframe = document.createElement('iframe');
			iframe.style.width = '100%';
			iframe.style.height = '100%';
			iframe.srcdoc = htmlContent; // Use the fetched HTML content as the iframe's source

			iframe.addEventListener('load', () => {
				const doc = iframe.contentDocument;

				// Create a synthetic contextmenu event to probe existing right-click handlers
				const testEvt = new MouseEvent('contextmenu', {
					bubbles   : true,                   // let the event bubble up the DOM hierarchy
					cancelable: true,                   // allow handlers to call preventDefault()
					view      : iframe.contentWindow    // bind the event to the iframe's Window object
				});

				const wasCanceled = !doc.dispatchEvent(testEvt);   // false  ⇒ aucun handler n’a annulé
				console.log("Context menu event was canceled:", wasCanceled);
				console.log("Context menu event injected:", doc.__neoContextInjected);

				/* 2.  Si personne n’a bloqué le clic-droit, on ajoute le nôtre  */
				if (!wasCanceled && !doc.__neoContextInjected) {   // flag interne pour éviter le doublon
					doc.addEventListener('contextmenu', handleContextMenu, { passive: false });
					doc.__neoContextInjected = true;
				}
			});

			if (!shouldCancelHtml) {
				viewer.appendChild(iframe);
			} else {
				console.log('append viewer with iframe cancelled');
			}
		} catch (error) {
			console.error('Error fetching HTML content:', error);
		}
		shouldCancelHtml = true;
		blinking.style.display = 'none';
	}

	async function showImage(file: FileData) {
		shouldCancelImage = false;
		abortController = new AbortController();
		await tick(); // Attend la fin du rendu
		viewer.innerHTML = ''; // Vide le conteneur
		blinking.style.display = 'block';

		try {
			const response = await fetch(file.url, {signal: abortController.signal});
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			const blob = await response.blob();
			const imageUrl = URL.createObjectURL(blob);

			const img = document.createElement('img');
			img.style.width = '100%';
			img.src = imageUrl; // Utilise l'URL de l'image comme source de l'élément img
			
			if (!shouldCancelImage) {
				viewer.appendChild(img);
			} else {
				console.log('append viewer with image cancelled');
			}
		} catch (error) {
			console.error('Error fetching image content:', error);
		}
		shouldCancelImage = true;
		blinking.style.display = 'none';
	}

	async function showMarkdown(file: FileData) {
		shouldCancelMarkdown = false;
		abortController = new AbortController();
		await tick(); // Attend la fin du rendu
		viewer.innerHTML = ''; // Vide le conteneur
		blinking.style.display = 'block';

		try {
			const response = await fetch(file.url, {signal: abortController.signal});
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			let markdownContent = await response.text();

			// Vérifie l'extension du fichier
			const extensionMatch = file.path.match(/\.(\w+)$/);
			if (extensionMatch) {
				const extension = extensionMatch[1];
				console.log("fichier .", extension);
				if (codeFormats.includes(`.${extension}`)) {
					markdownContent = `\`\`\`${extension}\n${markdownContent}\n\`\`\``;
				}
			}
			// Crée dynamiquement un composant Svelte
			if (!shouldCancelMarkdown) {
				new MarkdownCode({
					target: viewer,
					props: {
						message: markdownContent,
						latex_delimiters: [],
						sanitize_html : true,
						render_markdown: true,
						line_breaks: false,
						root: root,
					}
				});
			} else {
				console.log('append viewer with markdown cancelled');
			}
		} catch (error) {
			console.error('Error fetching Markdown content:', error);
		}
		shouldCancelMarkdown = true;
		blinking.style.display = 'none';
	}


	async function next_file() {
		await tick(); // Attend la fin du rendu
		blinking.style.display = 'none';
		if (Array.isArray(value) && value.length > 1) {
			index_of_file_to_show = (index_of_file_to_show + 1) % value.length;
		}
 	}

	async function previous_file() {
		await tick(); // Attend la fin du rendu
		blinking.style.display = 'none';
		index_of_file_to_show = (index_of_file_to_show - 1 + value.length) % value.length;
 	}

</script>


<Block {visible} {elem_id} {elem_classes} {container} {scale} {min_width} {height}>
	{#if loading_status}
		<StatusTracker
			autoscroll={gradio.autoscroll}
			i18n={gradio.i18n}
			{...loading_status}
			on:clear_status={() => gradio.dispatch("clear_status", loading_status)}
		/>
	{/if}
		<div class="viewer-container">
			<div bind:this={blinking} class="viewer-blinker" style="display: none">
				<span>·</span><span>·</span><span>·</span>
			</div>
			<div bind:this={viewer} on:contextmenu={handleContextMenu} class="viewer"></div>
			{#if showContextMenu}
				<button class="context-menu"
					style="top:{menuY}px; left:{menuX}px"
					on:click|stopPropagation={downloadFile}>
					{download_title}
				</button>
			{/if}
			<div class="button-row">
				{#if Array.isArray(value) && value.length > 1}
					<button class="left-arrow" on:click={previous_file} title={previous_file_title}>
						<svg xmlns="http://www.w3.org/2000/svg" width="80%" height="80%" viewBox="0 0 24 24">
							<path d="M15 6L8 12L15 18" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
						</svg>
					</button>
				{/if}
				{#if Array.isArray(value) && value.length > 0}
					<span class="file-name">&nbsp;&nbsp;&nbsp;{value[index_of_file_to_show].orig_name}&nbsp;&nbsp;&nbsp;</span>
				{:else if typeof value === 'string'}
					<span class="file-name">&nbsp;&nbsp;&nbsp;{value.orig_name}&nbsp;&nbsp;&nbsp;</span>
				{/if}
				{#if Array.isArray(value) && value.length > 1}
					<button class="right-arrow" on:click={next_file} title={next_file_title}>
						<svg xmlns="http://www.w3.org/2000/svg" width="80%" height="80%" viewBox="0 0 24 24">
							<path d="M9 6L16 12L9 18" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
						</svg>
					</button>
				{/if}
			</div>
		</div>
	<style>
		.viewer-container {
			position: relative;
			overflow: hidden;
			height: 100%;
			width: 100%;
			display: flex;
			flex-direction: column;
		}
		.viewer {
			display: flex;
			flex-direction: column;
			width: 100%;
			height: 100%;
			overflow: auto;
		}
		.error-message {
			position: absolute;
			top: 50%;
			left: 50%;
			transform: translate(-50%, -50%);
			text-align: center;
		}
		.viewer canvas {
			margin: .1vh 0;
		}
		.button-row {
			display: flex;
			flex-direction: row;
			width: 100%;
			justify-content: center;
			align-items: center;
		}
		.file-name {
			max-width: 90%;
			overflow: hidden;
			text-overflow: ellipsis;
			white-space: nowrap;
		}
		.viewer-blinker {
			position: absolute;
			top: 50%;
			left: 50%;
			transform: translate(-50%, -50%);
			color: var(--neo-blue);
			animation: blinker 1.5s cubic-bezier(.5, 0, 1, 1) infinite alternate;
			font-size: 3em;
		}
		.viewer-blinker span {
			opacity: 0;
			animation-name: blinker;
			animation-duration: 1.5s;
			animation-timing-function: cubic-bezier(.5, 0, 1, 1);
			animation-iteration-count: infinite;
		}
		.viewer-blinker span:nth-child(1) {
			animation-delay: 0s;
		}
		.viewer-blinker span:nth-child(2) {
			animation-delay: .5s; /* Délai pour le deuxième point */
		}
		.viewer-blinker span:nth-child(3) {
			animation-delay: 1s; /* Délai pour le troisième point */
		}
		.context-menu  {
			position:fixed;
			background-color:var(--button-secondary-background-fill) !important; 
			border-radius: var(--button-large-radius) !important;
			padding:var(--button-large-padding) !important;
			font-size:var(--button-large-text-size) !important;
			font-weight:var(--button-large-text-weight) !important;
			box-shadow: var(--button-secondary-shadow) !important;
			min-width: 190px;
			z-index:10000;
        }
		.left-arrow, .right-arrow {
			width: 22px;
			height: 22px;
			cursor: pointer;
			border-radius: 50%;
			fill: none;
			background-color:var(--button-secondary-background-fill) !important;
			display: flex;
			flex-shrink: 0;
			justify-content: center;
			align-items: center;
			stroke:var(--button-secondary-text-color);
			stroke-width: 17 !important;
			box-shadow: var(--button-secondary-shadow);
			z-index: var(--layer-1);
		}
		.textLayer {
			pointer-events: auto !important;
			user-select: text;
		}
		canvas {
			pointer-events: none;
		}
	</style>
</Block>
