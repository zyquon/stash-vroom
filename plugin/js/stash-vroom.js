;(function() {
    const baseURL = document.querySelector("base")?.getAttribute("href") ?? "/"

    const callGQL = (query, variables) => {
        variables = variables || {}
        const body = {query, variables}

        return fetch(`${baseURL}graphql`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(body),
        })
        .then(res => res.json())
        .then(res => res.data)
    }

    const getConfig = async () => {
        const pluginId = `VRoom`
        const query = `query Configuration { configuration { plugins } }`
        const response = await callGQL(query)
        const raw_config = response.configuration.plugins?.[pluginId] ?? {}

        // Now walk the keys and vals and if the key matches ^[a-z]_, then remove the prefix.
        // Those prefixes are just to enforce order in the UI.
        const config = {}
        for (const key in raw_config) {
            const val = raw_config[key]
            const newKey = key.replace(/^[a-z]_/, "")
            config[newKey] = val
        }
        return config
    }

    // window.getConfig = getConfig
    // window.callGQL = callGQL
    console.log(`Vroom is running...`)
})();