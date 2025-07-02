import React from 'react'

const base_url = document.querySelector("base")?.getAttribute("href") ?? "/"
const api_url = `${base_url}graphql`

export const callGQL = (query, variables=null) => {
    variables = variables || {}
    const body = {query, variables}

    return fetch(api_url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    })
    .then(res => res.json())
    .then(res => res.data)
}

export const useGQL = (query, variables=null) => {
    const [data, setData] = React.useState(null)
    const [error, setError] = React.useState(null)
    const [loading, setLoading] = React.useState(true)

    React.useEffect(() => {
        setLoading(true)
        callGQL(query, variables)
            .then(data => {
                setData(data)
                setLoading(false)
            })
            .catch(err => {
                setError(err)
                setLoading(false)
            })
    }, [query, JSON.stringify(variables)])

    return { data, error, loading }
}