import App from './App.svelte';

import { routes } from 'svelte-hash-router';
// import components
import Docviewer from "./Docviewer/Docviewer.svelte";
import Modelviz from "./Modelviz/Modelviz.svelte";
import ModelRefinement from "./ModelRefinement/ModelRefinement.svelte";

routes.set({
	'/': Modelviz,
	'/doc/:id': Docviewer,
	'/codes': ModelRefinement,
})

const app = new App({
	target: document.body
});

export default app;