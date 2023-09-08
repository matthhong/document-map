<script>
    import { onMount } from "svelte";
    import {
        Tile,
		Form,
        FormGroup,
        Slider,
        Button
	} from "carbon-components-svelte";

    import { sampledocs, sampleIndex } from "../Docviewer/stores.js";

    export let num_docs = 0;
    let sample_doc_ids = [];
    let sample_size = 10;

    function generateSample() {
        sample_doc_ids = Array.from({length: sample_size}, () => Math.floor(Math.random() * num_docs));
        sampledocs.set(sample_doc_ids);
        sampleIndex.set(0);
        console.log($sampledocs)

        window.location.href = "#/doc/" + $sampledocs[0];
    }
</script>

<Tile>
    <Form on:submit={generateSample}>
        <FormGroup>
            <Slider
                labelText='Sample N documents (2615 total)'
                min={1}
                max={30}
                bind:value={sample_size}
            />
        </FormGroup>

        <Button size="field" type="submit">Get a random sample</Button>
    </Form>
</Tile>