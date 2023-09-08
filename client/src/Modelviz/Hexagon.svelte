<script>
    export let width;
    export let color = "#000";
</script>

<div class=hexagone style="--width: {width}px; --color: {color};">
    <div class=left></div>
    <div class=rectangle></div>
    <div class=right></div>
</div>

<style>
    .hexagone {
        display: flex;
    }
    .left, .right {
            border-bottom: calc(var(--width)/2) solid transparent;
            border-top: calc(var(--width)/2) solid transparent;
    }
    .left {
        border-right: calc(var(--width)/3.464) solid  var(--color);
    }
    .right {
        border-left: calc(var(--width)/3.464) solid  var(--color);
    }
    .rectangle {
            width: calc(var(--width)/1.732);
            height: var(--width);
            background: var(--color);
    }
</style>