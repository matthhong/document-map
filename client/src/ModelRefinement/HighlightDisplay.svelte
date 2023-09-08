<script>
    import { CodeSnippet } from "carbon-components-svelte";
    import {
        ClickableTile,
        Tile,
        Grid,
        Row,
        Column,
    } from "carbon-components-svelte";

    import { selectedHighlights } from './store.js';
    import { codes } from '../store.js';
import { afterUpdate, onMount } from "svelte";

    export let displayhighlights = [];
    export let highlightWords = [];

    afterUpdate(() => {
        let test = document.getElementsByClassName("highlighttext")
        console.log(test);

        [...test].forEach(text_element => {
            highlightWords.forEach((query) => {
            let new_str = text_element.innerHTML.replace(
                query,
                '<span style="background-color:rgba(120, 169, 255, 0.3);" >' +
                    query +
                    "</span>"
            );
            text_element.innerHTML = new_str;
            })
        })
    })

</script>

<div class="highlightscroll" role="group" aria-label="selectable tiles">
    {#each displayhighlights as highlightobj, i}
        <ClickableTile
            light
            href={'/#/doc/' + highlightobj.doc_id}
            on:select={(e) => {
                selectedHighlights.set([displayhighlights[i], ...$selectedHighlights]);
            }}
            on:deselect={(e) => {
                let obj = displayhighlights[i];
                selectedHighlights.set($selectedHighlights.filter(item => item !== obj));
            }}
            value={"highlight" + i}
        >
            <Grid fullWidth>
                <Row padding>
                    <Column>
                        <h5>{highlightobj.doc_title}</h5>
                    </Column>
                </Row>
                <Row>
                    <Column>
                        <Tile>
                            <div class="highlighttext">
                                {highlightobj.highlight}
                            </div>
                        </Tile>
                    </Column>
                </Row>
                {#if highlightobj.memo != ""}
                    <Row>
                        <Column>
                            <Tile light>
                                <div class="memotext">
                                    {highlightobj.memo}
                                </div>
                            </Tile>
                        </Column>
                    </Row>
                {/if}
                <!-- {#if highlightobj.codes.length != 0}
                    <Row padding>
                        <Column>
                            <div class="codedisplay">
                                <strong>Codes:</strong>
                                {#each highlightobj.codes as code}
                                    <div class="codeitem">
                                        {code}
                                    </div>
                                {/each}
                            </div>
                        </Column>
                    </Row>
                {/if} -->
            </Grid>
        </ClickableTile>
    {/each}
</div>

<style>
    .highlightrow {
        margin-top: 20px;
        margin-bottom: 20px;
        padding: 10px;
        cursor: pointer;
    }
    .highlighttext {
        margin-top: 10px;
        line-height: 1.5;
    }
    .codeitem {
        padding: 5px;
        margin: 5px;
        display: inline-flex;
    }
    .highlightscroll {
        height: 60vh;
        overflow: auto;
        padding: 0 20px 0 20px;
    }
    .memotext {
        margin-left: 10px;
        font-size: 14px;
        font-style: italic;
    }
    .highlighttext {
        font-size: 16px;
    }
    .codedisplay {
        margin-top: 10px;
    }
</style>
