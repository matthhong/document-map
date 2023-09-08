<script>
    import { Grid, Row, Column } from "carbon-components-svelte";
    import KeywordSidebar from "./KeywordSidebar.svelte";
    import CodeInfo from "./CodeInfo.svelte";

    import {selectedHighlights, selectedWords, highlightedWords} from "./store.js";
    import { selectedCode, highlights, codes } from "../store.js";
import { afterUpdate } from "svelte";

    async function stripHighlights(texts) {
        const res = fetch(`./strip`, {
            method: "post",
            body: JSON.stringify(texts),
            headers: { "Content-Type": "application/json" },
        }).then((val) => {
            return val.json();
        });

        const text = await res;

        return text;
    }

    let currentCode1 = -1;
    let currentCode2 = -1;
    let currentHighlight;

    console.log($codes);

    if ($codes.length > 0) {
        currentCode1 = 0
    }


    // selectedHighlights.subscribe(() => {
    //     async function stripHighlights(texts) {
    //         const res = fetch(`./strip`, {
    //             method: "post",
    //             body: JSON.stringify(texts),
    //             headers: { "Content-Type": "application/json" },
    //         }).then((val) => {

    //             let text = val.json();

    //             return text;
    //         }).then((text) => {
    //             selectedWords.set(text.content)
    //         });

    //     }
        
    //     if ($selectedHighlights.length > 0) {
    //         let pooledHighlights = "";
    //         $selectedHighlights.forEach((highlight) => {
    //             pooledHighlights = pooledHighlights.concat(
    //                 highlight.highlight + " "
    //             );
    //         });
    //         stripHighlights(pooledHighlights)
    //     } else {
    //         selectedWords.set($highlightedWords)
    //     }
    // })

    async function getData() {
        let pooledHighlights = "";
        $highlights.forEach((highlight) => {
            pooledHighlights = pooledHighlights.concat(
                highlight.highlight + " "
            );
        });
        let pooledWords = await stripHighlights(pooledHighlights);

        highlightedWords.set(pooledWords.content);
        // selectedWords.set($highlightedWords)

        return pooledWords;
    }

    let promise = getData();

    afterUpdate(() => {
        console.log(currentCode1);
    })
</script>

<Grid fullWidth>
    <Row>
        <Column lg={2}>
            <Row>
				<label for="keyword-sidebar" class:bx--label={true}> See similar documents by keywords</label>
			</Row>
            {#await promise then response}
                <KeywordSidebar id="keyword-sidebar" currentCodes={[currentCode1, currentCode2]}/>
            {/await}
        </Column>
        <Column lg={7}>
            <CodeInfo bind:currentCodeId={currentCode1} bind:currentHighlight={currentHighlight} />
        </Column>
        <Column lg={7}>
            <CodeInfo bind:currentCodeId={currentCode2} bind:currentHighlight={currentHighlight}/>
        </Column>
    </Row>
</Grid>
