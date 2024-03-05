<script>
	import { onMount, onDestroy } from "svelte";
	import { params } from "svelte-hash-router";
	import { sampledocs, back, sampleIndex } from "./stores.js";
	import { highlights, visitedDocs } from "../store.js";

	import CodingBox from "./CodingBox.svelte";

	import {
		Grid,
		Row,
		Column,
		Button,
		Modal,
		PaginationNav,
	} from "carbon-components-svelte";

	import { fade, fly } from "svelte/transition";

	sampledocs.useLocalStorage();
	visitedDocs.useLocalStorage();
	sampleIndex.useLocalStorage();

	// from stores get what the last page was for the back button
	let button_str = "";
	if ($back == "#/") {
		button_str = "Document Map";
	} else if ($back == "#/codes") {
		button_str = "Model Refinement";
	}

	// Define variables
	let codingBox;
	let doc_id = $params.id;
	let text = { title: "", content: "" };
	let existing_highlights = $highlights;

	// highlight listener variables
	let highlight_start = -1;
	let highlight_end = -1;
	let highlightdisplay = "";

	let hovered = false;
	let h_clicked = false;
	let h_hover;
	let clicked_id = -1;

	// svelte objects
	let docContent;

	// random sample variables
	let sample_idx = $sampleIndex;

	// Event listeners for highlighting
	let watchList = [];
	function handleSelectionChange() {	
		if (watchList.length === 0) return;
		var selection = window.getSelection();

		if (!selection.containsNode(watchList[0], true)) return;

		if (selection.toString().length === 0) {
			codingBox.reset();
			return;
		}

		var selDir = getSelectionDir(selection);
		var startNode, endNode, startPos, endPos;
		if (selDir === 1) {
			startNode = selection.anchorNode;
			endNode = selection.focusNode;
			startPos = selection.anchorOffset;
			endPos = selection.focusOffset;
		} else {
			startNode = selection.focusNode;
			endNode = selection.anchorNode;
			startPos = selection.focusOffset;
			endPos = selection.anchorOffset;
		}

		if (!(textNodeIsWatched(startNode) & textNodeIsWatched(endNode)))
			return;

		var rangeStart = textNodeIsWatched(startNode)
			? roundSelectionIndex(startNode, 0, startPos)
			: startPos - 1;
		var rangeEnd = textNodeIsWatched(endNode)
			? roundSelectionIndex(endNode, 1, endPos)
			: endPos;
		var r = document.createRange();
		r.setStart(startNode, rangeStart + 1);
		r.setEnd(endNode, rangeEnd);
		selection.removeAllRanges();
		selection.addRange(r);

		highlight_start = r.startOffset;
		highlight_end = r.endOffset;
		const value = selection.toString();

		highlightdisplay = value;
	}

	function mouseDownListener(e) {
		if (e.which == 1 && e.target.id == "doccontent") {
			document.getSelection().removeAllRanges();
			let text_element = document.querySelector("#doccontent");
			// let test = text_element.innerHTML;
			// let new_str = test.replace(
			// 	'<span class="seen" style="background-color:#E65131; color:white;">' +
			// 		highlightdisplay +
			// 		"</span>",
			// 	highlightdisplay
			// );
			// console.log(new_str);
			text_element.innerHTML = text.content
		} else {
			// don't remove range if outside of content div
			e.preventDefault();
		}
	}

	function mouseUpListener(e) {
		if (e.target.id.indexOf("highlight") != -1) {
			document.getSelection().removeAllRanges();
			if (h_clicked) {
				h_hover.style.backgroundColor = "rgba(120, 169, 255, 0.3)"; // reset color of previous clicked highlight
				h_hover = e.target; // set current highlight to clicked highlight
				h_hover.style.backgroundColor = "rgba(120, 169, 255, 1)"; // set color of clicked highlight
				clicked_id = parseInt(e.target.id.slice(9));
				highlightdisplay = $highlights[clicked_id]["highlight"];
			} else {
				clicked_id = parseInt(e.target.id.slice(9));
				highlightdisplay = $highlights[clicked_id]["highlight"];
				h_clicked = true;
			}
		} else {
			if (h_clicked && e.target.id == "doccontent") {
				// if user clicked off highlight within content div, reset
				h_clicked = false;
				h_hover.style.backgroundColor = "rgba(120, 169, 255, 0.3)";
				hovered = false;
				clicked_id = -1;
				codingBox.reset();
			}

			// check for any new highlight selections
			if (e.which == 1 && e.target.id == "doccontent") {
				handleSelectionChange();
			}
		}

		if (e.target.id == "doccontent") {
			let text_element = document.querySelector("#doccontent");
			let test = text_element.innerHTML;
			let new_str = test.replace(
				highlightdisplay,
				'<span class="seen" style="background-color:#E65131; color:white;" >' +
					highlightdisplay +
					"</span>"
			);
			text_element.innerHTML = new_str;

			apply_persistent_highlights(text_element)
			e.preventDefault();
		}
	}

	function mouseOverListener(e) {
		if (!h_clicked) {
			if (e.target.id.indexOf("highlight") != -1) {
				hovered = true;
				h_hover = e.target;
				h_hover.style.backgroundColor = "rgba(120, 169, 255, 1)";
			} else {
				if (hovered) {
					h_hover.style.backgroundColor = "rgba(120, 169, 255, 0.3)";
					hovered = false;
				}
			}
		}
	}

	function getSelectionDir(sel) {
		var range = document.createRange();
		range.setStart(sel.anchorNode, sel.anchorOffset);
		range.setEnd(sel.focusNode, sel.focusOffset);
		if (
			range.startContainer !== sel.anchorNode ||
			(sel.anchorNode === sel.focusNode &&
				sel.focusOffset < sel.anchorOffset)
		)
			return -1;
		else return 1;
	}
	function roundSelectionIndex(textNode, nodeId, idx) {
		var isStart = nodeId === 0;
		var contents = textNode.textContent;
		var nearestSpaceIdx = -1;
		if (isStart) {
			nearestSpaceIdx = contents.lastIndexOf(" ", idx);
			if (nearestSpaceIdx === -1) nearestSpaceIdx = -1;
		} else {
			nearestSpaceIdx = contents.indexOf(" ", idx);
			if (nearestSpaceIdx === -1) nearestSpaceIdx = contents.length;
		}
		return nearestSpaceIdx;
	}
	function textNodeIsWatched(textNode) {
		return watchList.indexOf(textNode.parentElement) > -1;
	}

	// Highlight listener -----------------------------------------------------------------------------
	// https://stackoverflow.com/questions/34963610/how-can-i-highlight-a-word-term-quicker-and-smarter
	let WordJumpSelection = (function () {
		var WordJumpSelection = {
			stopWatching: function (elem) {
				console.log(watchList);
				var wlIdx = watchList.indexOf(elem);
				if (wlIdx > -1) watchList.splice(wlIdx, 1);
				console.log(watchList);
			},
			watch: function (elem) {
				var elems = Array.prototype.slice.call(
					typeof elem.length === "number" ? elem : arguments
				);
				if (watchList.length === 0) {
					WordJumpSelection.init();
				}
				elems.forEach(function (elem) {
					if (watchList.indexOf(elem) === -1) {
						watchList.push(elem);
					}
				});
			},
			init: function () {
				document.documentElement.addEventListener(
					"mousedown",
					mouseDownListener
				);

				document.documentElement.addEventListener(
					"mouseup",
					mouseUpListener
				);

				// listener for hovering over previous highlights -- changes color on mouseover
				document.documentElement.addEventListener(
					"mouseover",
					mouseOverListener
				);

				WordJumpSelection.init = function () {};
			},
		};
		return WordJumpSelection;
	})();

	// END Highlight listener -------------------------------------------------------------------------

	// Persistent Highlighting ------------------------------------------------------------------------
	function apply_persistent_highlights(text_element) {
		// check if the document has highlights
		if (existing_highlights.length != 0) {
			// only highlights for this doc_id
			for (let i = 0; i < existing_highlights.length; i++) {
				if (existing_highlights[i]["doc_id"] == doc_id) {
					let test = text_element.innerHTML;
					let query = existing_highlights[i]["highlight"];
					let new_str = test.replace(
						query,
						'<span id="highlight' +
							i +
							'" style="cursor:pointer; background-color:rgba(120, 169, 255, 0.3);" >' +
							query +
							"</span>"
					);
					text_element.innerHTML = new_str;
				}
			}
		}
	}
	// END Peristent highlight functions --------------------------------------------------------------

	// Random sample doc change
	function rs_change_doc() {
		doc_id = $sampledocs[sample_idx];
		console.log(sample_idx);
		window.location.hash = '#/doc/'+doc_id
		sampleIndex.set(sample_idx)
		getText(doc_id).then(() => setUp(doc_id));
	}

	// get text and tags from api at index doc_id
	async function getText(doc_id) {
		const res_text = await fetch(`./text/${doc_id}`);
		text = await res_text.json();
		return text;
	}
	async function getTags(doc_id) {
		const res_tags = await fetch(`./tags/${doc_id}`);
		tags = await res_tags.json();
	}

	function setUp(docId) {
			visitedDocs.set([...$visitedDocs, +docId])

			let el = document.querySelector("#doccontent");

			document.getSelection().removeAllRanges();
			el.innerHTML = text.content
			codingBox.reset();

			apply_persistent_highlights(el);

			if (existing_highlights.length > 0) {
				for (let i = 0; i < existing_highlights.length; i++) {
					if (existing_highlights[i]["doc_id"] == docId) {
						document.getElementById("highlight" + i).onclick = (
							ev
						) => {
							highlightdisplay = ev.target.innerHTML;
						};
					}
				}
			}

			el.addEventListener("contextmenu", (e) => e.preventDefault());
	}

	// on start get first text file
	onMount(async () => {
		let el = document.querySelector("#doccontent");
		WordJumpSelection.watch(el);
		getText(doc_id).then(() => setUp(doc_id));
		// getTags(doc_id);
	});

	onDestroy(() => {
		console.log("destroy");
		WordJumpSelection.stopWatching(document.querySelector("#doccontent"));

		document.documentElement.removeEventListener(
			"mousedown",
			mouseDownListener
		);

		document.documentElement.removeEventListener(
			"mouseup",
			mouseUpListener
		);

		// listener for hovering over previous highlights -- changes color on mouseover
		document.documentElement.removeEventListener(
			"mouseover",
			mouseOverListener
		);
	});
</script>

<div id="viewport" in:fade={{ duration: 500 }}>
	<Grid fullWidth padding>
		<!-- {#if button_str != ""}
			<Row>
				<div class="returnbutton">
					<Button
						size="small"
						on:click={() => {
							window.location.href = $back;
						}}
					>
						{"Return to " + button_str}
					</Button>
				</div>
			</Row>
		{/if} -->
			<Row>
				<div class="returnbutton">
					<Button
						size="small"
						on:click={() => {
							window.location.href = '#/';
						}}
					>
						Return to Document Map
					</Button>
				</div>
			</Row>
		<Row>
			<Column>
				<Row id="text-header-row">
					<Column lg={8}>
						<h3 class="doctitle">{text.title}</h3>
					</Column>
					<Column lg={8}>
						<div class="pagination">
							{#if $sampledocs.length != 0}
								<PaginationNav
									bind:page={sample_idx}
									total={$sampledocs.length}
									shown={10}
									on:change={rs_change_doc}
								/>
							{:else}
								<PaginationNav total={1} />
							{/if}
						</div>
					</Column>
				</Row>
				<Row>
					<div
						id="doccontent"
						bind:this={docContent}
						spellcheck="false"
						class="divscroll"
						style="height: 300px;"
					>
						{text.content}
					</div>
				</Row>
			</Column>
		</Row>
		<Row>
			<CodingBox
				bind:this={codingBox}
				bind:doc_id
				{highlight_start}
				{highlight_end}
				bind:highlightdisplay
				bind:highlight_id={clicked_id}
			/>
		</Row>
	</Grid>
</div>

<style>
	.doctitle {
		position: relative;
		padding-left: 5px;
		float: left;
		line-height: 1;
	}
	.divscroll {
		height: 28vw;
		width: 100%;
		/* background-color: white; */
		font: 16px/26px Georgia, Garamond, Serif;
		overflow: auto;
		position: relative;
	}
	.pagination {
		position: relative;
		float: right;
	}
	.returnbutton {
		padding-bottom: 20px;
	}
</style>
