<script>
    import { onMount } from 'svelte';

    import {
        Column,
        Row,
        Tile,
        ExpandableTile
    } from "carbon-components-svelte";

    export let open = false;

    let doc_head;
    let current_title = "";
    let current_head = "";

    onMount(async () => {
        const response = await fetch(`./documenthead`);
		doc_head =  await response.json();
    })

    export function update_doc_info(nw_doc_id){
        current_title = doc_head[nw_doc_id].title;
        current_head = doc_head[nw_doc_id].head;
    }
</script>

<!-- <Row padding>
    <Column>
        <Tile>
            {"Document Cluster Info"}
        </Tile>
    </Column>
</Row> -->
<Row padding>
    <Column>
        <ExpandableTile bind:expanded={open} tileExpandedLabel="Right-click to reset" tileCollapsedLabel="Right-click to view details">
            <div slot="above" style="height: 3rem">
                {current_title}
            </div>
            <div slot="below" style="height:26rem">
                {current_head}
            </div>
          </ExpandableTile>
    </Column>
</Row>