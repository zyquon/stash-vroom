import React from "react"
import parse from 'html-react-parser'
import DOMPurify from "dompurify"

const PluginApi = window.PluginApi
// const GQL = PluginApi.GQL
const StashService = PluginApi.utils.StashService

const PLUGIN_ID = `VRoom`

// const PlusIcon = PluginApi.libraries.FontAwesomeSolid.faPlus;
const config_defaults = {
  a_vrTagName: "VR",
  b_skipDependencyCheck: false,
  c_doImages: false,
  d_doMarkerSurfing: false,
  e_markerSurfingDuration: 15,
  f_markerSurfingRandom: false,
}

const SetDefaultConfig = ({ vroom_config }) => {
  console.log(`Set default config, current config:`, vroom_config)
  const [updatePluginConfig, qUpdatePluginConfig] = StashService.useConfigurePlugin()

  console.log(`qUpdatePluginConfig:`, qUpdatePluginConfig)
  if ( qUpdatePluginConfig.loading ) {
    // Updates are already underway
    console.log(`Updating plugin configuration is loading`)
    return <div>Updating plugin configuration...</div>
  }

  const new_config = get_vroom_config_default_updates(vroom_config)
  console.log(`vroom config updates:`, new_config)
  if (! new_config ) {
    console.log(`No updates needed`)
    return <div>Config is good</div>
  }

  if ( qUpdatePluginConfig.called ) {
    console.log(`UpdatePluginConfig was called, wait for new props to arrive`)
    return <div>Config is being updated...</div>
  }

  console.log(`Updating plugin configuration`, {vroom_config, new_config})
  if ( qUpdatePluginConfig.called ) {
    console.log(`Okay the value of .loading is:`, qUpdatePluginConfig.loading)
    throw new Error(`UpdatePluginConfig was already called, this should not happen.`)
  }
  updatePluginConfig({
    variables: {
      plugin_id: PLUGIN_ID,
      input: new_config,
    },
  })
  .then((result) => {
    console.log(`Plugin configuration updated`, result)
    return result
  })

  console.log(`Returning null from SetDefaultConfig`)
  return null
}

const Documentation = () => {
  const [content, setContent] = React.useState(null)
  const [inFlight, setInFlight] = React.useState(false)

  if ( !content ) {
    if (! inFlight) {
      // Fetch the HTML and then 
      setInFlight(true)
      fetch(`/plugin/${PLUGIN_ID}/assets/docs/index.html`)
        .then((response) => {
          if (!response.ok) {
            throw new Error(`Failed to fetch documentation: ${response.statusText}`);
          }
          return response.text();
        })
        .then((html) => {
          const allowed_tags = [
            "a", "p", "h1", "h2", "h3", "h4", "h5", "h6",
            "body",
            "ul", "ol", "li", "strong", "em", "code", "pre",
            "blockquote", "div", "span", "table", "thead", "tbody",
            "tr", "th", "td", "img", "br", "hr",
            "dl", "dt", "dd", "section", "article",
            "nav", "aside", "header", "footer",
          ]
          // const sanitizedHtml = DOMPurify.sanitize(html, { ALLOWED_TAGS: ["a", "p", "h1", "h2", "h3", "ul", "li", "strong", "em"] });
          // Allow all the tags that Sphinx uses when generating python documentation.
          let sanitizedHtml = DOMPurify.sanitize(html, { ALLOWED_TAGS: allowed_tags, ALLOWED_ATTR: ["href", "src", "alt", "title", "class"] })
          // sanitizedHtml = `<div>Hello world</div>`
          console.log(`Sanitized HTML:`, sanitizedHtml)
          const safeTree = parse(sanitizedHtml)
          console.log(`Parsed HTML tree:`, safeTree)
          setContent(safeTree);
          setInFlight(false);
        })
    }

    return <div>Loading documentation...</div>
  }

  console.log(`Okay the content is:`, content)
  return <div className="documentation-content">
    {content}
  </div>
}

export default () => {
  // For a reason I do not know, PerformerSelect works but LoadingIndicator does not. Scene works as does SceneCard
  // Maybe the usable ones are here: https://github.com/stashapp/stash/blob/develop/ui/v2.5/src/pluginApi.tsx
  // const res = PluginApi.hooks.useLoadComponents([PluginApi.loadableComponents.LoadingIndicator])
  // if (res) {
  //   console.log(`Components are loading`)
  //   return null
  // }
  console.log(`Stash VRoom: render`)

  const { LoadingIndicator } = PluginApi.components;
  const qConfig = StashService.useConfiguration()

  if ( qConfig.loading ) {
    console.log(`Configuration is loading`)
    return <>
      <h1>Stash VRoom</h1>
      <LoadingIndicator />
    </>
  }

  const vroom_config = get_vroom_config(qConfig.data.configuration)
  console.log(`Current vroom config:`, vroom_config)

  return <>
    <h1>Stash VRoom</h1>
    <SetDefaultConfig vroom_config={vroom_config} />

    <Documentation />
  </>

  // TODO:
  // I think just return if it's loading. Then if it's updating return an updating content.
  // Might have to call some kind of reloadconfig helper if the qConfig does not reflect the updated settings.
  // const [ready, setReady] = React.useState()
  // Also for debugging maybe render a button that clicking does the update, to avoid the infinite loops
  // Or maybe there is a dedicated component called SetDefaults or something and it can just do the update
  // logic and render out a string of its state or something
}

const get_vroom_config = (stash_config, is_local=false) => {
  const vroom_config = JSON.parse(JSON.stringify(stash_config.plugins.VRoom || {}))

  if (is_local) {
    // Iterate through all keyvals and if the key has a prefix of a letter and underscore then strip that. So "a_foo":42 becomes "foo":42
    for (const key in vroom_config) {
      const match = key.match(/^([a-zA-Z])_(.*)$/)
      if (match) {
        const new_key = match[2]
        vroom_config[new_key] = vroom_config[key]
        delete vroom_config[key]
      }
    }
  }

  return vroom_config
}

const get_vroom_config_default_updates = (vroom_config) => {
  // Return an object to update with defaults populated, or null if it is not needed.
  const update = {}

  for (const key in config_defaults) {
    const default_val = config_defaults[key]
    const current_val = vroom_config[key]

    if (current_val === undefined) {
      update[key] = default_val
    } else if (typeof default_val === "string") {
      if (! current_val) {
        update[key] = default_val
      }
    } else if (typeof default_val === "boolean") {
      if (typeof current_val !== "boolean") {
        update[key] = default_val
      }
    } else if (typeof default_val === "number") {
      if (typeof current_val !== "number") {
        update[key] = default_val
      }
      else if (key == 'e_markerSurfingDuration' && current_val <= 0) {
        update[key] = default_val
      }
    } else {
      throw new Error(`Unknown config value type for ${key} of type ${typeof default_val} with current value of ${current_val} (${typeof current_val})`)
    }
  }

  if (Object.keys(update).length == 0)
    return null

  const new_config = JSON.parse(JSON.stringify(vroom_config))
  for (const key in update)
    new_config[key] = update[key]
  return new_config
}

  // const [loading, setLoading] = React.useState(true);
  // const [error, setError] = React.useState<Error | null>(null);
  // const [code, setCode] = React.useState(sql);
  // const [columns, setColumns] = React.useState([]);
  // const [rows, setRows] = React.useState([]);
  // const [querySQL, { loading, error }] = useQuerySQLMutation({
  //   onCompleted: (data) => {
  //     if (data?.querySQL) {
  //       setColumns(data.querySQL.columns);
  //       setRows(data.querySQL.rows);
  //     } else {
  //       setColumns([]);
  //       setRows([]);
  //     }
  //   },
  //   onError: () => {
  //     setColumns([]);
  //     setRows([]);
  //   },
  // });

  // const submitQuery = () => {
  //   try {
  //     querySQL({ variables: { sql: code } });
  //   } catch (e) {
  //     console.error("Failed to decode or query SQL:", e);
  //   }
  // };

  // function classNames(...classes) {
  //   return classes.filter(Boolean).join(" ");
  // }

  // return (
  //   <div className="px-4 sm:px-6 lg:px-8 mb-16">
  //     <div className="sm:flex sm:items-center">
  //       <div className="sm:flex-auto">
  //         <h1 className="text-base font-semibold text-gray-50">
  //           Stash VRoom
  //         </h1>
  //       </div>
  //       <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-2/3">
  //         Editor goes here
  //         {/* <Editor
  //           value={code}
  //           onValueChange={(code) => setCode(code)}
  //           highlight={(code) => highlight(code, languages.sql, "sql")}
  //           padding={10}
  //           className="editor"
  //         /> */}
  //       </div>
  //     </div>

  //     <div className="flex justify-end mt-4">
  //       {/* <button disabled={loading}>
  //         <PlusIcon />
  //         {loading ? "Running..." : "Submit Query"}
  //       </button> */}
  //       <Button className="minimal d-flex align-items-center h-100 btn btn-primary" title="Loading: {loading}">
  //         XXX
  //       </Button>
  //     </div>

  //     {error && (
  //       <div className="my-4 p-4 bg-red-800/20 ring-1 ring-red-500 rounded-lg text-red-300">
  //         <h3 className="font-bold">Error</h3>
  //         <pre className="whitespace-pre-wrap">{error.message}</pre>
  //       </div>
  //     )}

  //     <div className="relative -mx-4 mt-10 ring-1 ring-stash-700 sm:mx-0 sm:rounded-lg text-lg text-gray-50 bg-stash-600 shadow-lg shadow-stash-900">
  //       {loading && (
  //         <div className="absolute inset-0 bg-stash-800/50 flex items-center justify-center rounded-lg">
  //           <LoadingIndicator />
  //         </div>
  //       )}
  //     </div>
  //   </div>
  // );