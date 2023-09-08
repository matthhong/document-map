<script>
    import { onMount, getContext, afterUpdate } from "svelte";
    import Keyword from "./Keyword.svelte";
    import Tooltip from "./Tooltip.svelte";
    import TextNewLine16 from "carbon-icons-svelte/lib/TextNewLine16";
    import { hiddenClusters, clusters, highlightedWords, selectedWords } from "../store.js";
    import { modelHistoryIndex } from "../../store.js"

    hiddenClusters.useLocalStorage();
    modelHistoryIndex.useLocalStorage();

    export let expanded = true;
    export let name;
    export let children;
    export let level_id;
    export let level;

    export let highlighted = false;
    // export let level;

    const wordsFromCluster = getContext("words");
    const pooledWords = getContext("pooledWords");

    // afterUpdate(() => {
    //     console.log($clusters)
    // })

    // let show_cluster;
    // if (level >= 3) {
    //     show_cluster = true;
    // } else {
    //     show_cluster = $clusters[level.toString()].has(level_id);
    // }

    // function toggle() {
    //     expanded = !expanded;

    //     if (expanded) {
    //         hiddenClusters.set($hiddenClusters.filter((v) => v != name));
    //     } else {
    //         hiddenClusters.set([...$hiddenClusters, name]);
    //     }
    // }

    // if ($hiddenClusters.includes(name)) {
    //     // expanded = false;
    // }

    let words = [];
    let allWords = [];


        // if (children.length <= 0) {
        //     window.wordsFromCluster = $wordsFromCluster;
        //     allWords = $wordsFromCluster[level_id].words;
        //     // words = allWords
        //     words = [...allWords].filter((x) => $pooledWords.includes(x));
        // }

        if (children.length <= 0) {
            allWords = $wordsFromCluster["0"][level_id].words;
            // words = allWords
            words = [...allWords].filter((x) => $pooledWords.includes(x));
            console.log(words);
        }

    function toggleHighlight() {
		highlighted = !highlighted;
	}

    import { sampledocs, sampleIndex } from "../../Docviewer/stores.js";

    sampledocs.useLocalStorage();
	sampleIndex.useLocalStorage();
    sampledocs.reset();
	sampleIndex.set(0);
    let sample_size = 30;

    function generateSample() {
        sample_doc_ids = Array.from({length: sample_size}, () => Math.floor(Math.random() * num_docs));
        sampledocs.set(sample_doc_ids);
        sampleIndex.set(0)
        // console.log($sampledocs)

        window.location.href = "#/doc/" + $sampledocs[0];
    }

    async function sampleDocsByCluster() {
        d3.json(
			new URL("./files/p_tw_d_" + $modelHistoryIndex + ".json", import.meta.url),
            function (data) {
                let p_tw_for_d = data[level][level_id].map((e, i) => [i, e])
                p_tw_for_d.sort((a, b) => b[1] - a[1])
                window.p_tw_for_d = p_tw_for_d
                sampledocs.set(p_tw_for_d.map(e => e[0]).slice(0,30));
                sampleIndex.set(0)
                console.log($sampledocs);
                window.location.href = "#/doc/" + $sampledocs[0];
            }
        )
    }

    afterUpdate(() => {
        children = children.map((e) => {
                e.highlighted = highlighted;
                return e;
            })

        if (children.length <= 0) {
            allWords = $wordsFromCluster["0"][level_id].words;
            // words = allWords
            words = [...allWords].filter((x) => $pooledWords.includes(x));
            console.log(words);
        }
    })
</script>

<!-- {#if show_cluster} -->
<span 
    class={highlighted ? 'highlighted' : ''}
    data-tip="I am a tool tip"
    on:mouseenter={() => {
        if (name != 'Root') {
            toggleHighlight() 
        }
    }}
	on:mouseleave={() => {
        if (name != 'Root') {
            toggleHighlight() 
        }
    }}
    on:click={sampleDocsByCluster}
>
    {#if name != 'Root'}
    <Tooltip title={$wordsFromCluster[level][level_id].words.slice(0, 10).join(",")+"..."}>
        <TextNewLine16 />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <!-- {name + ' ' + level_id} -->
    </Tooltip>
        
    {:else}
        <span style="font-size: 13px; font-style:italic; pointer-events: none; ">Select a keyword cluster...</span>
    {/if}
</span>
<!-- {/if} -->

{#if expanded && name}
    <ul style="border-left: 1px solid {highlighted ? '#0353E9' : '#eee'};">
        {#if children.length > 0}
            {#each children as cluster}
                <li>
                    <svelte:self {...cluster} />
                </li>
            {/each}
        {:else}
            {#each words as kw}
                <li>
                    <Keyword name={kw} highlighted={highlighted}/>
                </li>
            {/each}
        {/if}
    </ul>
{/if}

<style>
    span {
        /* padding: 0 0 0 1.5em; */
        cursor: pointer;
    }

    span:hover::after {
        position: absolute;
        content: attr(data-tooltip);
        bottom: -2.5em;
        right: -1em;
        background-color: #333;
        color: white;
        padding: .25em .5em;
        font-size: .8em;
    }

    /* .expanded {
        background-image: url(/tutorial/icons/folder-open.svg);
    } */

    .highlighted {
        color: #0353E9;
    }

    ul {
        padding: 0 0 0 0.5em;
        margin: 0 0 0 0.5em;
        list-style: none;
        border-left: 1px solid #eee;
    }

    li {
        /* padding: 0.2em 0; */
    }
</style>
