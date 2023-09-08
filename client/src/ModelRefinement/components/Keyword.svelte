<script>
    import {Checkbox} from 'carbon-components-svelte';

	export let name;
	export let highlighted;
	$: type = name.slice(name.lastIndexOf('.') + 1);
</script>

<p class={highlighted ? 'highlighted-keyword' : ''}>&nbsp;&nbsp;&nbsp;&nbsp;{name}</p>

<style>
	.keyword {
		padding: 0 0 0 1.5em;
		background: 0 0.1em no-repeat;
		background-size: 1em 1em;
	}

	.highlighted-keyword {
		color:blue;
	}
</style>
