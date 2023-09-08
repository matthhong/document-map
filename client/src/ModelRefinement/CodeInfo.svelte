<script>
    import { Grid, Row, Column, CodeSnippet } from "carbon-components-svelte";
    import { setContext } from "svelte";
    import { highlightedWords } from "./store";
    import { selectedCode, highlights, codes } from "../store.js";
    import HighlightDisplay from "./HighlightDisplay.svelte";
    import KeywordSidebar from "./KeywordSidebar.svelte";
    import CodeFilter from "./CodeFilter.svelte"

    export let currentCodeId = -1;

    let highlightsDisplay = [];
    $: {
        if (currentCodeId > -1) {
            let currentCode = $codes[currentCodeId]
            highlightsDisplay = $highlights.filter(obj => obj.codes.includes(currentCode.code))
        }
    }
</script>



<Grid fullWidth>
    <Row>
        <Column>
            <CodeFilter bind:currentCodeId={currentCodeId}/>
        </Column>
    </Row>
    <Row>
        <Column>
            {#if currentCodeId > -1}
                <HighlightDisplay displayhighlights={highlightsDisplay} highlightWords={ $codes[currentCodeId].words.split(',') }/>
            {/if}
        </Column>
    </Row>
</Grid>
