<script>
    import { onMount, afterUpdate } from "svelte";
    import {
        Form,
        FormGroup,
        Grid,
        Row,
        Column,
        RadioButtonGroup,
        RadioButton,
        Button,
        TextArea,
        ComboBox,
    } from "carbon-components-svelte";
    import { selectedCode, highlights, codes } from '../store.js'
import { transform } from "topojson-client";

    let highlightinfo = $highlights;

    let currentCode = {};
    export let currentCodeId;
    let memoinput = "";
    let categories = [];
    let currentCategoryName = "";
    let newCodeName = ''

    let currentCategoryId = -1;


    if (currentCodeId > -1) {
        currentCode = $codes[currentCodeId];
        currentCategoryName = currentCode.category;
        currentCategoryId = parseInt(currentCode.category_id);
        memoinput = currentCode.memo;
        newCodeName = currentCode.code
    }


    let update_cat = false;
    let update_memo = false;
    let update_code = false;

    let formDisabled = false;

    async function getData () {
        // load codeinfo: code category and code memo

        const response2 = await fetch(`./getcategories`);
        categories = await response2.json();

        return categories;
    }
    let codeResponse = getData();

    async function submitForm() {
        // check if code is selected
        if (currentCode === {}) {
            console.log("No code detected");
            return;
        }


        if (currentCode.category != currentCategoryName) {
            update_cat = true;
        }
        console.log(update_cat);

        if (currentCode.code != newCodeName) {
            update_code = true;
        }

            console.log(update_cat);
            console.log(currentCategoryName);
        // check if new memo created or edited, or if memo unchanged do nothing
        if (update_memo || update_cat || update_code) {
            const response = await fetch(`./addcodecategory`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    code_id: currentCode.id,
                    code_name: newCodeName,
                    category: currentCategoryName,
                    category_id: currentCategoryId,
                    memo: memoinput,
                    update: update_cat,
                }),
            });
        }
        // if changes occured, save to files and adjust coloring
        update_codeinfo();
        // if no changes occured do nothing, pop-up saying nothing has changed
    }

    async function update_codeinfo() {
        // load codeinfo: code category and code memo
        const response1 = await fetch(`./getcodeinfo`)
            .then((response) => response.json())
            .then((response) => {
                codes.set(response);
                console.log($codes)
                return response;
            });

        const response2 = await fetch(`./getcategories`)
            .then((response) => response.json())
            .then((response) => {
                categories = response;
                console.log(categories)

                return response;
            });

        return response1;
    }

    // $: memoArea.value = currentCode.memo

</script>

<div class="formmargin">
    {#await codeResponse then res}
        <Form on:submit={submitForm}>
            <FormGroup>
                <ComboBox
                    titleText="Retrieve code"
                    placeholder="Select code"
                    items={$codes.map((code) => {
                        code.text = code.code;
                        return code
                    })}
                    bind:selectedIndex={currentCodeId}
                    on:select={(e) => {
                        console.log(currentCodeId);
                        
                        currentCode = e.detail.selectedItem;
                        currentCategoryName = e.detail.selectedItem.category;
                        currentCategoryId = parseInt(e.detail.selectedItem.category_id)
                        newCodeName = e.detail.selectedItem.text;
                        memoinput = e.detail.selectedItem.memo;
                        formDisabled = false;
                        // memoArea.value = currentCode.memo
                    }}
                    on:clear={(e) => {
                        currentCode = {};
                        currentCategoryName = "";
                        currentCategoryId = -1;
                        newCodeName = ''
                        memoinput = ''
                        // memoArea.value = "Enter new memo..."
                        formDisabled = true;
                    }}
                    on:keyup={(e) => {
                        newCodeName = e.target.value;

                        if (newCodeName == '') {
                            formDisabled = true;
                        }
                    }}
                />
            </FormGroup>
            <FormGroup>
                <ComboBox
                    titleText="Categorize code"
                    placeholder="Enter new category or select from existing"
                    bind:selectedIndex={currentCategoryId}
                    items={categories}
                    on:select={(e) => {
                        currentCategoryName = e.detail.selectedItem.text;
                        formDisabled = false;
                    }}
                    on:keyup={(e) => {
                        currentCategoryName = e.target.value;
                        currentCategoryId = -1;
                        if (currentCategoryName == '') {
                            formDisabled = true;
                        } else {
                            formDisabled = false;
                        }
                    }}
                    on:clear={() => {
                        currentCategoryName = "";
                        currentCategoryId = -1;
                        formDisabled = true;
                    }}
                />
            </FormGroup>

            <FormGroup>
                    <TextArea
                        style="resize: none;"
                        labelText="Write memo for code"
                        bind:value={ memoinput }
                        on:input={(e) => {
                            update_memo = true;
                        }}
                    />
            </FormGroup>

            <div class="submitbutton">
                <Button size="small" kind="secondary" type="submit" disabled={formDisabled}>Confirm</Button>
            </div>
        </Form>
    {/await}
</div>

<style>
    .submitbutton {
        float: right;
    }
    .formmargin {
        margin-bottom: 80px;
    }

    :global(.codeCheckbox) {
        display: inline-block !important;
        margin-right: 12px;
    }
</style>
