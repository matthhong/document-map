<script>
    import Cluster from "./components/Cluster.svelte";
    import { afterUpdate, onMount } from "svelte";

    import { setContext } from "svelte";
    import { writable } from "svelte/store";

    let data = writable();
    setContext("words", data);

    import { clusters, highlightedWords, selectedWords } from "./store.js";
    import { Content } from "carbon-components-svelte";
import { codes, modelHistoryIndex } from "../store";

modelHistoryIndex.useLocalStorage();


    let component;
    let cluster_ids;

    export let currentCodes;
    
    let pooledWordsData = writable();
    setContext('pooledWords', pooledWordsData)

    let treeData;
    let wordTree;
    let wordsToClusterData;
    async function getTopicData() {
        let res = d3
            .queue()
            .defer(d3.json, "./files/topic_saliency_hashed_" + $modelHistoryIndex + ".json")
            .defer(d3.json, "files/sbm_topic_tree_" + $modelHistoryIndex + ".json")
            .defer(d3.json, "files/words_to_cluster_" + $modelHistoryIndex + ".json")
            .await(function (error, topics, tree_data, words_to_cluster) {
                if (error) {
                    console.error("Oh dear, something went wrong: " + error);
                } else {
                    // const mappedData = d3.map(topics, (d) => d.topic_id);
                    data.set(topics);
                    wordsToClusterData = words_to_cluster;

                    treeData = tree_data
                    wordTree = createTree(tree_data);
                }
            });

        return res;
    }

    let dataPromise = getTopicData();

    function createTree(tree) {
        let root = tree;
        
        let pooledWords = $codes.filter((e, i) => currentCodes.includes(i)).map((code) => code ? code.words.split(',') : []).flat().filter((e) => e.length>0)
        console.log(pooledWords);
        pooledWordsData.set(pooledWords)

        let newRoot = { name: "Root", children: [] };

        if (pooledWords.length > 0) {
            let cluster_dict;
            let refined_clusters = {};

            [...Array(3).keys()].forEach((element) => {
                refined_clusters[element] = [];
            });

            for (
                let index = 0;
                index < pooledWords.length;
                index++
            ) {
                const word = pooledWords[index];
                cluster_dict = wordsToClusterData[word];

                Object.keys(refined_clusters).forEach((element) => {
                    refined_clusters[element].push(cluster_dict[element]);
                });
            }

            Object.keys(refined_clusters).forEach((element) => {
                refined_clusters[element] = new Set(refined_clusters[element]);
            });
            clusters.set(refined_clusters);
            window.clusters = refined_clusters;

            function addNode(node, parent) {
                var newNode;
                if (refined_clusters[node.level].has(parseInt(node.level_id))) {
                    newNode = {
                        name: node.name,
                        children: [],
                        level_id: node.level_id,
                        level: node.level
                    };
                    parent.children.push(newNode);

                    if (node.children) {
                        node.children.forEach((el) => {
                            addNode(el, newNode);
                        });
                    }
                }
            }

            if (root) {
                root.children.forEach((el) => {
                    addNode(el, newRoot);
                });
            }
            component = Cluster;

            return newRoot;
        }
        return newRoot;
    }
    
    afterUpdate(() => {
        console.log(currentCodes);
        if (wordsToClusterData) {
            wordTree= createTree(treeData);
        }
    })

</script>

    {#await dataPromise then response}
        <svelte:component this={component} {...wordTree} />
    {/await}
<!-- <Cluster {...root}/> -->
