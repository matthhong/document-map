<script>
	import "carbon-components-svelte/css/all.css";

	import { Header, HeaderAction, HeaderActionLink, HeaderUtilities, HeaderPanelLink, HeaderPanelDivider, HeaderPanelLinks, Modal } from "carbon-components-svelte";
	import Information20 from "carbon-icons-svelte/lib/Information20/Information20.svelte";
	import LogoGithub20 from "carbon-icons-svelte/lib/LogoGithub20/LogoGithub20.svelte";

	import { onMount, setContext } from "svelte";
	import { Router } from "svelte-hash-router";

	import Docviewer from "./Docviewer/Docviewer.svelte";
	import Modelviz from "./Modelviz/Modelviz.svelte";

	setContext('colorScheme', ["#66c2a5","#fc8d62","#8da0cb","#e78ac3","#a6d854","#ffd92f","#e5c494","#b3b3b3"])
	import {
		Content,
		Grid,
		Row,
		Column,
		Theme,
		RadioButtonGroup,
		RadioButton,
		Button,
		SkeletonPlaceholder
	} from "carbon-components-svelte";

	import { highlights } from "./store.js";


	fetch(`./createtables`, { method: "POST" });

	async function getData() {

		// const response2 = await fetch(`./getdoccodetable`);
		// doc_code_table = await response2.json();

		// const res = await fetch(`./gethighlightinfo`)
        // const objs = await res.json();

		// highlights.set(objs);

		return true;
	}

	let promise = getData();

	let themes = [
		{ label: "light", value: "white" },
		{ label: "dark", value: "g90" },
	];

	let theme = "white"; // "white" | "g10" | "g80" | "g90" | "g100"

	$: document.documentElement.setAttribute("theme", theme);

	const views = [Docviewer, Modelviz];

	let currentView = 1;

	// function toggleView(view) {
	// 	console.log(window.location.href)
	// 	if(view == 1) {
	// 		window.location.href = "#/";
	// 	}
	// 	else if (view == 2) {
	// 		window.location.href = "#/codes";
	// 	}
	// }
	function doc_map() {
		window.location.href = "#/";
	}
	function model_refinement() {
		window.location.href = "#/codes";
	}

	let modelUpdateDisabled = true;

	function run_model() {
		modelUpdateDisabled = true;
		
		fetch(`./run_model`, { method: "POST" })
			.then((res) => {
				if (res.status == 201) {
					modelUpdateDisabled = false;
				}
			});
	}

	let isSideNavOpen = false;
	let isOpen = false;
</script>

<Theme bind:theme persist persistKey="__carbon-theme" />

			<Header company="A Document Map of Blog Posts on" platformName="SimplyRecipes.com" bind:isSideNavOpen>
				<HeaderUtilities>
					<div on:click={() => (isOpen = true)} on:keydown>
						<HeaderActionLink icon={Information20}/>
					</div>
					<HeaderActionLink icon={LogoGithub20} href={"https://github.com/matthhong/document-map"} target="_blank"/>
				</HeaderUtilities>
			</Header>

			<Modal
				modalHeading=""
				passiveModal
				size="lg"
				bind:open={isOpen}
			>
				<p class="info">
					<strong>Scholastic</strong> is a tool for qualitative researchers to explore a collection of documents through interactive document clustering.
					<br>
					<br>

					The <strong>Document Map</strong> view is a geographical treemap representing hiearchical document clusters as spatial 'regions':

					<br>
					&nbsp;&nbsp;&nbsp;&nbsp;- You can control the granularity of the hieararchical clusters with the <em>step slider</em> (top left)
					<br>
					&nbsp;&nbsp;&nbsp;&nbsp;- You can select some N documents with the <em>random sampler</em> (top right)
					<br>
					<br>
					Each document is represented with a hexagonal tile:
					
					<br>
					&nbsp;&nbsp;&nbsp;&nbsp;- <em>Right-clicking</em> a hexagon expands a preview that shows the first 1,000 characters of the document.
					<br>
					&nbsp;&nbsp;&nbsp;&nbsp;- <em>Left-clicking</em> a hexagon opens the document in the <strong>Document Reader</strong>, where you can highlight and annotate the text.
				
					<br><br>

					Our paper describing the prototype and its evaluation is available at the following link:
					<a href="https://dl.acm.org/doi/pdf/10.1145/3526113.3545681" target="_blank">https://dl.acm.org/doi/pdf/10.1145/3526113.3545681</a>
					
					<br><br>
					The paper was presented at ACM UIST 2022:
				</p>

				<iframe width="800" height="450" src="https://www.youtube.com/embed/w0tn9ySpVMw?si=6ToqfN5PoYXIAhUg" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

				<br><br>
			</Modal>

<Content>

	<Grid fullWidth noGutter>
		<!-- <Row>
			<Column lg={2}>
				<RadioButtonGroup
					legendText="Color theme"
					bind:selected={theme}
				>
					{#each themes as theme}
						<RadioButton
							labelText={theme.label}
							value={theme.value}
						/>
					{/each}
				</RadioButtonGroup>
			</Column>
			<Column lg={2}>
				<Button on:click={doc_map} kind="primary" icon={Carbon32}
					>Navigate texts</Button
				>
			</Column>
			<Column lg={2}>
				<Button disabled on:click={model_refinement} kind="secondary" icon={ChartRelationship32}>Refine codes</Button>
			</Column>
			<Column lg={8}>
				<div class="layering">
					<DocCodeFilter
					/>
				</div>
			</Column>
			<Column lg={2}>
				<Button disabled={modelUpdateDisabled} on:click={run_model} kind="ghost" icon={TextMiningApplier32}>Update clusters</Button>
			</Column>
		</Row> -->
		<Row>
			<Column>
				<div style="margin: var(--cds-layout-03) 0;">
					{#await promise}
						<SkeletonPlaceholder style="width: 100%; height: 800px;"/>
					{:then res}
						<Router />
					{/await}
				</div>
			</Column>
		</Row>
	</Grid>
</Content>

<style>
	:root {
		font-size: 16px;
		@media (max-width: 1640px) {
			font-size: 14px;
		}
	}
	.layering {
		position: relative;
		z-index: 10000;
	}
	.info {
		font-size: 1.25rem;
	}
	.iframe {
		/* Center it in the parent component */
		margin: 0 auto;
		display: block;
	}
</style>
