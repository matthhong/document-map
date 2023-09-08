<script>
    import {
        Tile,
        Row,
        Column,
        Checkbox
	} from "carbon-components-svelte";

    import Hexagon from "./Hexagon.svelte";

    export let pin_toggle;

    export let togglePins = () => {};
</script>

<Tile>
<div style="padding-left:20px">
    <Row padding>
        <h6>Legend</h6>
    </Row>
    <Row padding>
        <Column md={2}>
            <Hexagon width={20} color={"#000"}/>
        </Column>
        <Column md={6}>
            <div>Coded Documents</div>
        </Column>
    </Row>
    <Row padding>
        <Column md={2}>
            <Hexagon width={20} color={"#DDDDDD"}/> 
        </Column>
        <Column md={6}>
            <div>Visited Documents</div>
        </Column>
    </Row>
    <Row padding>
        <Column md={2}>
            {#if pin_toggle}
                <span style="font-size: 2em;"><i class="fa-solid fa-location-dot"></i></span>
            {:else}
                <span style="font-size: 2em; opacity: 0.1;"><i class="fa-solid fa-location-dot"></i></span>
            {/if}
        </Column>
        <Column md={6}>
             
            {#if pin_toggle}
                <div style="padding-top: 10px;">Code</div>
            {:else}
                <div style="opacity: 0.1; padding-top: 10px;">Code</div>
            {/if}
        </Column>
    </Row>
    <Row padding>
        <Checkbox 
            labelText="Toggle Pins"
            checked = true
            on:change={() => {
                pin_toggle = !pin_toggle;
                console.log(pin_toggle);
                togglePins();
            }}
        />
    </Row>
</div>
</Tile>