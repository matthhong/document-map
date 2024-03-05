<script>
	import "carbon-components-svelte/css/all.css";
	import TextMiningApplier32 from "carbon-icons-svelte/lib/TextMiningApplier32";
	import ChartRelationship32 from "carbon-icons-svelte/lib/ChartRelationship32";
	import Carbon32 from "carbon-icons-svelte/lib/Carbon32";

	import { onMount, setContext } from "svelte";
	import { Router } from "svelte-hash-router";

	import Docviewer from "./Docviewer/Docviewer.svelte";
	import Modelviz from "./Modelviz/Modelviz.svelte";
	import ModelRefinement from "./ModelRefinement/ModelRefinement.svelte";
	import DocCodeFilter from "./DocCodeFilter.svelte";

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

	const views = [Docviewer, Modelviz, ModelRefinement];

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
</script>

<Theme bind:theme persist persistKey="__carbon-theme" />

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
</style>
