<script>
	import { afterUpdate } from "svelte";

	import {
		Row,
		Column,
		Tag,
		TextArea,
		TextInput,
		Button,
	} from "carbon-components-svelte";

	import { highlights, codes } from "../store.js";

	export let highlight_start;
	export let highlight_end;
	export let doc_id;
	export let highlightdisplay;
	export let highlight_id = -1;

	let highlightcodes = [];
	let memo = "";
	let words;
	let fill_highlight;
	let highlight_arr = [];
	let highlight_words = [];
	let stripped;

	let old_hd = "";
	let old_hid = highlight_id;
	// Function to clear all inputs externally
	export function reset() {
		highlightdisplay = "";
		highlight_arr = [];
		highlight_words = [];
		highlightcodes = [];
		memo = "";
	}

	let codeInput = '';
	let saving = false;

	// update function -- autofill for previous highlight or initialize memo and highlight codes variables
	export function update() {

		if (highlight_id != -1) {
			fill_highlight = $highlights[highlight_id];
			memo = fill_highlight["memo"];
			words = fill_highlight["words"];
			highlightcodes = fill_highlight["codes"];
		} else {
			memo = "";
			highlightcodes = [];
		}
		if (highlightdisplay != "") {
			get_stripped_highlight(highlightdisplay).then(() => {
				highlight_arr = stripped["content"];
				// highlight_words = highlight_arr;
			});
		} else {
			reset();
		}
		old_hd = highlightdisplay;
		old_hid = highlight_id;
	}

	// save highlight on button click to api
	function savehighlight() {
		// save highlight and codes
		if (highlight_id == -1) {
			fetch(`./addcodehighlight`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({
					id: highlight_id,
					highlight: [highlight_start, highlight_end],
					codes: highlightcodes,
					doc_id: doc_id,
					memo: memo,
					words: highlight_words,
				}),
			}).then(() => {
				// getCodeInfo();
				location.reload();
			});
		}
	}

	// function getCodeInfo() {
    //     return fetch(`./getcodeinfo`)
    //         .then((response) => response.json())
    //         .then((response) => {
    //             codes.set(response);
	// 			location.reload();
    //             return response;
    //         });
    // }

	// FUNCTIONS FOR CODE SELECTION ------------------------------------------------------------------
	// Get and initialize all codes
	// let existingCodes;
	async function getCodes() {
		return await fetch("/codes").then((response) => {
			let existingCodes = response.json();
			return existingCodes;
		});
	}
	let existingCodePromise = getCodes();

	function add(code) {
		highlightcodes = [code];
	}

	function update_codes(code) {
		if (code != "") {
			var exists = false;
			for (let i = 0; i < highlightcodes.length; i++) {
				if (highlightcodes[i] == code) {
					exists = true;
					break;
				}
			}
			if (!exists) {
				add(code);
			}
		}
		// if (!exists) {
		// 	add(code);
		// }
	}

	function resetCodeInput(input) {
		input.value = "";
	}

	function deleteCode(code) {
		let idx = highlightcodes.indexOf(code);
		if (idx > -1) {
			highlightcodes.splice(idx, 1);
			highlightcodes = highlightcodes;
		}
	}
	// END: FUNCTIONS FOR CODE SELECTION -------------------------------------------------------------

	// FUNCTIONS FOR IMPORTANT WORDS -----------------------------------------------------------------
	async function get_stripped_highlight(h) {
		const strip_response = await fetch(`./strip`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify(h),
		});
		stripped = await strip_response.json();
	}

	function select_hword(h_word, remove) {
		if (remove) {
			highlight_words.splice(highlight_words.indexOf(h_word), 1);
		} else {
			highlight_words.push(h_word);
		}
	}
	// END: FUNCTIONS FOR IMPORTANT WORDS ------------------------------------------------------------

	afterUpdate(async () => {
		if (highlightdisplay != old_hd || highlight_id != old_hid) {
			update();
		}
	});
</script>

<Column>
	{#if highlight_arr.length > 0}
		<Row>
			<label for="highlightdiv" class:bx--label={true}>
				Choose important words
			</label>
		</Row>
	{/if}
	<Row>
		<div id="highlightdiv">
			<p>
				{#each highlight_arr as h_word, i}
					<span
						style="cursor:pointer; background-color:rgba(120, 169, 255, 0); text-decoration: underline;"
						on:click={(e) => {
							console.log(e.target.style.backgroundColor);
							
							if (
								e.target.style.backgroundColor ==
								"rgba(120, 169, 255, 0.3)"
							) {
								console.log("turn to blue");
								
								e.target.style.backgroundColor =
									"rgba(120, 169, 255, 0)";
								select_hword(h_word, true);
							} else {
								e.target.style.backgroundColor =
									"rgba(120, 169, 255, 0.3)";
								select_hword(h_word, false);
							}
						}}
					>
						{h_word}
					</span>
					{" "}
				{/each}
			</p>
		</div>
	</Row>
	<div style="margin: var(--cds-layout-03) 0;" />
	<Row>
		<label for="code-list" class:bx--label={true}> Codes </label>
	</Row>
	<Row>
		<div id="code-list">
			{#each highlightcodes as code}
				<Tag filter type="cyan" on:close={deleteCode(code)}>
					{code}
				</Tag>
			{/each}
		</div>
		{#await existingCodePromise then existingCodes}
			{#if existingCodes.length > 0}
				{#each existingCodes[1] as code}
					{#if !(highlightcodes.includes(code))}
					<Tag
						interactive
						on:click={(e) => update_codes(e.target.innerText)}
					>
						{code}
					</Tag>
					{/if}
				{/each}
			{/if}
		{/await}
	</Row>
	<Row>
		<TextInput
			bind:value={codeInput}
			placeholder="Enter new code"
			on:click={(e) => e.target.focus()}
			on:keydown={(e) =>
				e.key === "Enter" &&
				update_codes(e.target.value) &&
				resetCodeInput(e.target)}
		/>
	</Row>
	<Row>
		<TextArea
			light
			on:click={(e) => e.target.focus()}
			bind:value={memo}
			placeholder="Memo this highlight"
			class="memoinput"
		/>
	</Row>
	<div style="margin: var(--cds-layout-03) 0;" />
	<Row>
	<Button
		disabled={highlightcodes.length > 0 || codeInput.length > 0 ? false : true}
		on:click={(e) => {
			e.target.disabled = true;
			console.log('???');
			
			update_codes(codeInput);
			savehighlight();
			
		}}
	>
		Save Highlight
	</Button>
</Row>
</Column>
