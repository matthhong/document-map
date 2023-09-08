<script>
    import { Tag, Row, Column, Form } from "carbon-components-svelte";
    import { getContext } from "svelte";
    import { selectedCode, codes, highlights } from "./store.js";

    async function getcodes() {
        // return await fetch(`./getcodeinfo`)
        //     .then((response) => response.json())
        //     .then((response) => {
        //         codes.set(response);
        //         return response;
        //     });
        return true;
    }
    let promise = getcodes();

    const colorScheme = getContext("colorScheme");

    function clear_selectedcodes() {
        selectedCode.set([]);
    }

    function addcodefilter(code) {
        let exists = false;
        for (let i = 0; i < $selectedCode.length; i++) {
            if (code.id == $selectedCode[i].id) {
                exists = true;
            }
        }
        if (!exists) {
            selectedCode.set([code, ...$selectedCode]);
        }
    }

    function deleteCode(id) {
        selectedCode.set($selectedCode.filter((el) => el.id !== id));
    }

    // if ($highlights.length > 0 && codeResponse != oldCodeResponse) {
    //     codeinfo = codeResponse.map((code) => {
    //         let count = 0;
    //         $highlights.forEach((hl) => {
    //             if (hl.codes.includes(code.code)) {
    //                 count++;
    //             }
    //         });
    //         code.count = count;
    //         return code;
    //     });
    //     oldCodeResponse = codeResponse;
    // }
    let codeinfo = [];
    codes.subscribe(() => {
        codeinfo = $codes;
    });
</script>

<Row>
    <Column>
        <Tag
            interactive
            type="outline"
            on:click={() => {
                // clear();
                clear_selectedcodes();
            }}
        >
            Clear code filters
        </Tag>
        {#each $selectedCode as scode}
            <Tag
                filter
                style="background-color: {colorScheme[parseInt(scode.category_id)]}" 
                on:close={deleteCode(scode.id)}
            >
                { scode.category_id == '0' ? scode.code : scode.category + ' - ' + scode.code }
            </Tag>
        {/each}
    </Column>
</Row>

<Row>
    <Column>
        {#await promise}
            <Tag skeleton />
            <Tag skeleton />
            <Tag skeleton />
        {:then promise}
            {#each codeinfo as code}
                <Tag
                    interactive
                    style="background-color: {colorScheme[parseInt(code.category_id)]}" 
                    on:click={() => {
                        addcodefilter(code);
                    }}
                >
                    { code.category_id == '0' ? code.code : code.category + ' - ' + code.code }
                </Tag>
            {/each}
        {/await}
    </Column>
</Row>
