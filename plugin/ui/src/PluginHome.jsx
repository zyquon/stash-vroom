import React from "react"

const PluginApi = window.PluginApi
// const GQL = PluginApi.GQL
const StashService = PluginApi.utils.StashService

const PLUGIN_ID = `VRoom`

// const PlusIcon = PluginApi.libraries.FontAwesomeSolid.faPlus
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

export default () => {
  // For a reason I do not know, PerformerSelect works but LoadingIndicator does not. Scene works as does SceneCard
  // Maybe the usable ones are here: https://github.com/stashapp/stash/blob/develop/ui/v2.5/src/pluginApi.tsx
  // const res = PluginApi.hooks.useLoadComponents([PluginApi.loadableComponents.LoadingIndicator])
  // if (res) {
  //   console.log(`Components are loading`)
  //   return null
  // }
  console.log(`Stash VRoom: render`)

  const { LoadingIndicator } = PluginApi.components
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
  </>
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