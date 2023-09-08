<script>
	import { afterUpdate, getContext, onMount } from "svelte";
	import { fade } from "svelte/transition";

	import * as d3 from "d3";
	import { createEventDispatcher } from "svelte";
	import { clusterLevel } from "./store.js";
	import { selectedCode, codes, highlights, visitedDocs, modelHistoryIndex } from "../store.js";
	import * as topojson from "topojson-client";
	import { sampledocs, back, sampleIndex } from "../Docviewer/stores.js";

	import {
		Grid,
		Row,
		Column,
		ProgressIndicator,
		ProgressStep,
		Button,
	} from "carbon-components-svelte";

	import ClusterMapSidebar from "./ClusterMapSidebar.svelte";
	import RandomSample from "./RandomSample.svelte";
	import Legend from "./Legend.svelte";

	const colorScheme = getContext("colorScheme");

	modelHistoryIndex.useLocalStorage();

	visitedDocs.useLocalStorage();

	// legend variables
	let pin_toggle = true;

	// sidebar related variables
	let doc_sidebar;
	let currentHex;
	let fixed = false;
	let open = false;
	let doc_id_hover = "0";

	// code filter variables
	let doc_code_table = [];
	let selected_docs = [];

	// topography data
	let topojsonData;

	// Persist current cluster depth level
	clusterLevel.useLocalStorage();
	sampledocs.reset();
	sampleIndex.set(0);

	$: document.documentElement.setAttribute("clusterLevel", clusterLevel);

	// Initialize SVG components (wrapper and the visualization)
	const svg = d3
		.create("svg")
		.attr("preserveAspectRatio", "xMinYMin meet")
		.attr("viewBox", "0 0 800 800")
		.attr("transform", "rotate(150 0 0) translate(30,70)")
		// Class to make it responsive.
		.classed("svg-content-responsive", true);

	const vis = svg.append("g").attr("transform", "translate(400,100)");

	// Hexagon specifications
	let radius = 6;
	let dx = radius * 2 * Math.sin(Math.PI / 3);
	let dy = radius * 1.5;
	let path_generator = d3.geoPath().projection(
		d3.geoTransform({
			point: function (x, y) {
				this.stream.point(
					(x * dx) / 2,
					(-(y - (2 - (y & 1)) / 3) * dy) / 2
				);
			},
		})
	);
	let enter;

	// boilerplate required to produce events
	const dispatch = createEventDispatcher();

	let num_docs = 0;
	let num_levels = 3;

	function colorDocuments() {
		const docs = selected_docs.map(d => d[0])
		const categories = selected_docs.map(d => d[1])
		d3.selectAll("path.hex")
			.transition()
			.duration(0)
			.style("fill", (d) => {
				const docIndex = docs.indexOf(d.properties.label)

				if (docIndex > 0) {
					return "#000000";
				} else if ($visitedDocs.includes(parseInt(d.properties.label))) {
					return "#DDDDDD";
				} else {
					return "#FFFFFF";
				}
			});
		
		var allDocs = []
		if(pin_toggle) {
			[...Array(8)].forEach((v, catIndex) => {
				var catIndices = categories.map((e, i) => e === catIndex ? i : '').filter(String)
				var selectedDocsForCategory = selected_docs.filter((v, i) => catIndices.includes(i)).map(d => d[0])
				allDocs = allDocs.concat(selectedDocsForCategory);

				var pins = d3.selectAll(".pin" + catIndex);

				pins.transition()
					.duration(0)
					.style("fill", (d) => {
						if (selectedDocsForCategory.includes(d.properties.label)) {
							return colorScheme[catIndex];
						}
					})
					// .attr("class", function(d) { 
					// 	var count = allDocs.filter(function(value){
					// 			return value === d.properties.label;
					// 		}).length;
						
					// 	if (count > 1) {
					// 		return 'pin' + catIndex + ' fa fa-circle-' + count
					// 	}
					// })
					
					.text(function(d) { 
						var count = allDocs.filter(function(value){
								return value === d.properties.label;
							}).length;
						if (count > 1) {
							return count
						} else if (count == 1 && selectedDocsForCategory.includes(d.properties.label)) {
							return '\uf041'
						}
				})
			})
		}
		

	}

	function togglePins() {
		const categories = selected_docs.map(d => d[1])
		if(pin_toggle) {
			colorDocuments();
		}
		else {
			[...Array(8)].forEach((v, catIndex) => {
			var pins = d3.selectAll(".pin" + catIndex);

			pins.transition()
				.duration(0)
				.style("fill", 0)
				.text("")
		})
		}
	}

	var codeMap = d3.map($codes, (d) => d.id);
	function updateDocuments() {
		selected_docs = [];
		for (let i = 0; i < doc_code_table.length; i++) {
			if ($selectedCode.length <= 0) {
				selected_docs.push([doc_code_table[i].doc_id, codeMap.get(doc_code_table[i].code_id).category_id]);
			} else {
				for (let j = 0; j < $selectedCode.length; j++) {
					const code = $selectedCode[j];

					if (code.id == parseInt(doc_code_table[i].code_id)	) {
						selected_docs.push([doc_code_table[i].doc_id, code.category_id]);
					}
				}
			}
		}

		selected_docs = Array.from(new Set(selected_docs));
	}
	selectedCode.subscribe(() => {
		updateDocuments();
		colorDocuments();
	});

	modelHistoryIndex.subscribe(() => {
		if (topojsonData) {
			location.reload()
		}
	})


	onMount(async () => {

		// const response2 = await fetch(`./getdoccodetable`);
		// doc_code_table = await response2.json();

		d3.json(
			new URL("./files/regions_depth_" + $modelHistoryIndex + ".topo.json", import.meta.url),

			function (error, data) {
				topojsonData = data;
				window.topojsonData = topojsonData;
				num_docs = topojson.feature(data, data.objects[num_levels]).features
					.length;
				num_levels = topojsonData.objects.depth.geometries.length - 1

				// Most things borrowed from http://bl.ocks.org/nitaku/8272715
				var whiteness = 0.6;
				var whiten = function (color) {
					return d3.interpolateHcl(
						color,
						d3.hcl(void 0, 0, 100)
					)(whiteness);
				};
				var defs, title;
				//   title = svg.append('text').attr('class', 'title').text(topojson.feature(data, data.objects['0']).features[0].properties.label).attr('transform', 'translate(80,40)');
				/* define the level zero region (the land)
				 */
				defs = svg.append("defs");

				// Draw outer boundary
				defs.append("path")
					.datum(
						topojson.feature(data, data.objects["0"]).features[0]
					)
					.attr("id", "land")
					.attr("d", path_generator);
				vis.append("use")
					.attr("class", "land-glow-outer")
					.attr("xlink:href", "#land");
				vis.append("use")
					.attr("class", "land-glow-inner")
					.attr("xlink:href", "#land");
				vis.append("use")
					.attr("class", "land-fill")
					.attr("xlink:href", "#land");


				// Draw individual document hexagons
				let hexShapes = vis
					.selectAll("path.hex")
					.data(topojson.feature(data, data.objects[num_levels]).features);

				enter = hexShapes
					.enter()
					.append("path")
					.attr("class", "hex")
					// .on("click", (d,i) => clicked(d))
					.on(
						"click",
						(d, i) => {
							sampledocs.reset();
							sampleIndex.set(0);
							back.set("#/");
							(window.location.href = "#/doc/" + d.properties.label);
						}
					)
					.on("mouseover", mover)
					.on("mouseout", mout)
					.on("contextmenu", rightclick)
					.attr("d", path_generator)
					.attr("fill", "#DDDDDD")
					.style("fill-opacity", 1)
					// .attr("stroke", "#DDDDDD")
					// .style("stroke-width", 1 / 2)
					.style("z-index", 1000)
					.style('cursor', 'pointer')
					.attr("id", (d, i) => {
						return "doc_id_" + d.properties.label;
					});

					
					// .text(function(d) { 
					// 	if (selected_docs.includes(d.properties.label)) {
					// 		return '\uf276'
					// 	} else {
					// 		return '\uf276'
					// 	}
					// }); 

				function mover(d) {
					if (!fixed) {
						d3.select(this)
							.transition()
							.duration(10)
							.style("fill", "#DDDDDD");

						currentHex = this;
						doc_id_hover = d.properties.label;
						document.querySelector(".sidebar").style.visibility =
							"visible";
						doc_sidebar.update_doc_info(parseInt(doc_id_hover));
					}
				}

				function mout(d) {
					if (!fixed) {
						d3.select(this)
							.transition()
							.duration(1000)
							.style("fill", () => {
								if ( $visitedDocs.includes(parseInt(d.properties.label))) {
									return "#DDDDDD";
								} else {
									return "#FFFFFF";
								}
							});
							

						currentHex = null;
						doc_id_hover = "0";
						document.querySelector(".sidebar").style.visibility =
							"hidden";
					}
				}

				function rightclick(d) {
					d3.event.preventDefault();
					fixed = !fixed;
					if (fixed) {
						open = true;
						// doc_sidebar.expand_doc_info(parseInt(doc_id_hover));
					} else {
						d3.select(currentHex)
							.transition()
							.duration(1000)
							.style("fill-opacity", 1);

						currentHex = null;
						doc_id_hover = "0";
						document.querySelector(".sidebar").style.visibility =
							"hidden";
						open = false;
					}
				}

				// Append visualization to SVG wrapper
				d3.select("div.chart").append(() => svg.node());

				updateDocuments();
				// colorBoundary();
				[...Array(3)].forEach((v, i) => {
					vis.append("path")
					.datum(
						topojson.mesh(
							data,
							data.objects[i+1],
							function (a, b) {
								return a !== b;
							}
						)
					)
					.attr("d", path_generator)
					.attr("class", "boundary " + "boundary"+(i+1))
					.style("stroke", "#444444")
					.style("stroke-width", "" + 1.8 / $clusterLevel + "px");
				})
				colorBoundary();
				drawPins(data);
				colorDocuments();
			}
		);
	});


	function drawPins(data) {
		// Draw pins
		if(pin_toggle) {
			[...Array(8)].forEach((v, i) => {
				vis.selectAll(".pin" + i)
					.data(topojson.feature(data, data.objects[num_levels]).features)
					.enter()
					.append('text')
					.attr('class', 'pin' + i)
					.attr('font-family', 'FontAwesome')
					.attr('font-size', function(d) { return '2em'} )
					.style('z-index', 99999999)
					.style('opacity', 1)
					.attr('transform', (d) => {
						var centroid = path_generator.centroid(d)
						return "translate(" + (centroid[0] + 5) + ',' + (centroid[1] + 12)  + ") rotate(210,0,0)";
					})
					.style('pointer-events', 'none')
		})
		}
	}

	function colorBoundary() {
		// Draw boundaries around each cluster
		// vis.select(".boundary" ).remove();

		[...Array(3)].every((v, i) => {

			if (i >= $clusterLevel) {
				vis.select(".boundary" + (i + 1))
					.transition()
					.style("opacity", 0)
				return true;
			}

			// Make sure you return true. If you don't return a value, `every()` will stop.
			vis.select(".boundary" + (i + 1))
					.transition()
					.style("opacity", 1)
			return true;
			
			// vis.append("path")
			// .datum(
			// 	topojson.mesh(
			// 		data,
			// 		data.objects[i+1],
			// 		function (a, b) {
			// 			return a !== b;
			// 		}
			// 	)
			// )
			// .attr("d", path_generator)
			// .attr("class", "boundary" + (i+1))
			// .style("stroke", "#444444")
			// .style("stroke-width", "" + (1.8 / 1) + "px");
		})
	}

	clusterLevel.subscribe(() => {
		if (topojsonData) {
			colorBoundary(topojsonData)
		}
	});
</script>

<Grid>
	<Row>
		<Column lg={3}>
			<Row>
				<label for="depth-layer" class:bx--label={true}> Adjust cluster boundary level</label>
			</Row>
			<Row>
			<ProgressIndicator id="depth-layer" vertical currentIndex={$clusterLevel - 1}>
				{#each Array(num_levels) as _, i}
					<ProgressStep
						label={i == num_levels ? "None" : "L" + (i + 1)}
						description="The progress indicator will listen for clicks on the steps"
						on:click={() => clusterLevel.set(i + 1)}
					/>
				{/each}
			</ProgressIndicator>
			</Row>
			<div style="margin: var(--cds-layout-01) 0;" />
			<Row>
				<label for="model-history" class:bx--label={true}>Model History</label>
			</Row>
			<Row>
			<ProgressIndicator id="model-history" vertical currentIndex={$modelHistoryIndex}>
				{#each Array(3) as _, i}
					<ProgressStep
						label={"Step " + i}
						description="The progress indicator will listen for clicks on the steps"
						on:click={() => modelHistoryIndex.set(i)}
					/>
				{/each}
			</ProgressIndicator>
			</Row>
			<Row>
				
				<Column>
					<div style="padding-top:20px;">
						<Legend 
							bind:pin_toggle={pin_toggle}
							togglePins = {togglePins}
						/>
					</div>
				</Column>
			</Row>
		</Column>
		<Column lg={9}>
			<Row>
				<label for="document-map" class:bx--label={true}> Explore and sample data </label>
			</Row>
				<div id="document-map" class="chart" />
		</Column>
		<Column lg={4}>
			<Row>
				<Column>
					<RandomSample bind:num_docs={num_docs} />
				</Column>
			</Row>
			<Row>
				<Column>
					<div class="sidebar">
						<ClusterMapSidebar
							bind:this={doc_sidebar}
							bind:doc_id={doc_id_hover}
							bind:open
						/>
					</div>
				</Column>
			</Row>
		</Column>
	</Row>
</Grid>

<style>
	.sidebar {
		visibility: hidden;
	}
	:global(#land) {
		fill: none;
	}

	:global(.land-glow-outer) {
		stroke: #eeeeee;
		stroke-width: 16px;
	}

	:global(.land-glow-inner) {
		stroke: #dddddd;
		stroke-width: 8px;
	}

	:global(.land-fill) {
		stroke: #444444;
		stroke-width: 2px;
	}

	:global(.boundary) {
		stroke: #444444;
		fill: none;
		pointer-events: none;
	}
</style>
