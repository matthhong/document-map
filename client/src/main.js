import App from './App.svelte';

import { routes } from 'svelte-hash-router';
// import components
import Docviewer from "./Docviewer/Docviewer.svelte";
import Modelviz from "./Modelviz/Modelviz.svelte";

routes.set({
	'/': Modelviz,
	'/doc/:id': Docviewer,
})

const app = new App({
	target: document.body
});

export default app;