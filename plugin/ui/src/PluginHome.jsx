import React from "react"

const PluginApi = window.PluginApi
const StashService = PluginApi.utils.StashService

const { Badge } = PluginApi.libraries.Bootstrap
const { Link, NavLink } = PluginApi.libraries.ReactRouterDOM

// Import the useGQL helper function which is exported from ./lib/gql.js.
import { useGQL } from "./gql.js"

//
// Local config
//

const PLUGIN_ID = `VRoom`
const PLUGIN_NAME = `VRoom`

// const PlusIcon = PluginApi.libraries.FontAwesomeSolid.faPlus
const CONFIG_DEFAULTS = {
  a_readWrite: false,
  b_skipDependencyCheck: false,
  c_doImages: false,
  d_doMarkerSurfing: false,
  e_markerSurfingDuration: 15,
  f_markerSurfingRandom: false,
}

const get_my_config = (stash_config, strip_prefix=false) => {
  const raw_config = JSON.parse(JSON.stringify(stash_config.plugins[PLUGIN_ID] || {}))
  const config = strip_prefix ? strip_prefix(raw_config) : raw_config

  // Insert "virtual" values reflecting settings from elsewhere in the system.
  config._trackActivity = stash_config.ui.trackActivity || false
  config._vrTag = (stash_config.ui.vrTag || '').trim()

  return config
}

const strip_prefix = (config) => {
  // Return a copy of the config with the prefixes stripped.
  const new_config = {}
  for (const key in config) {
    const match = key.match(/^([a-zA-Z]{1,2})_+(.*)$/)
    const new_key = match ? match[2] : key
    new_config[new_key] = config[key]
  }
  return new_config
}

const useMyConfig = (strip_prefix=false) => {
  const config_query = StashService.useConfiguration()
  if ( !config_query.called || config_query.loading || !config_query.data )
    return null

  console.log(`Stash config:`, config_query.data.configuration)
  const my_config = get_my_config(config_query.data.configuration, strip_prefix)
  return my_config
}

export default () => {
  console.log(`VRoom: render`)
  // For a reason I do not know, PerformerSelect works but LoadingIndicator does not. Scene works as does SceneCard
  // Maybe the usable ones are here: https://github.com/stashapp/stash/blob/develop/ui/v2.5/src/pluginApi.tsx
  // const res = PluginApi.hooks.useLoadComponents([PluginApi.loadableComponents.LoadingIndicator])
  // if (res) {
  //   console.log(`Components are loading`)
  //   return null
  // }

  const my_config = useMyConfig()
  console.log(`Current vroom config:`, my_config)

  const { Container } = PluginApi.libraries.Bootstrap
  return <Container style={{ fontSize: `1.2em` }}>
    <h1>Stash VRoom</h1>
    <Config my_config={my_config} />
    <Operation config={my_config} />
  </Container>
}

const useMainTag = ({ name }) => {
  const [ready, setReady] = React.useState(false)
  const [main_tag, setMainTag] = React.useState(null)

  const query = `
    query Tags($name: String!) {
      findTags(tag_filter: {name: {value: $name, modifier: EQUALS}}, filter: {per_page: 1}) {
        tags {
          id name sort_name
          children { id name sort_name children { id name sort_name children { id name sort_name children { id name sort_name children { id name sort_name children { id name sort_name children { id name sort_name children { id name sort_name children { id name sort_name children { id name sort_name } } } } } } } } } }
        }
      }
    }`

  const get_tags = useGQL(query, { name:name })
  if (!ready && !get_tags.loading && get_tags.data) {
    const found_tags = get_tags.data.findTags.tags
    if (found_tags.length == 0) {
      console.log(`Main tag name not found: ${JSON.stringify(name)}`)
      setMainTag(null)
      setReady(true)
    }

    setMainTag(found_tags[0])
    console.log(`Found main tag:`, name)
    setReady(true)
  }

  return { ready, tag:main_tag }
}

const Operation = ({ config }) => {
  if (! config)
    return null

  const cfg = strip_prefix(config)
  const { ready: main_tag_ready, tag: main_tag } = useMainTag({ name: cfg._vrTag })

  const followup = ( cfg && main_tag_ready && main_tag ) && <>
    <ReadWrite config={config} />
    <Startup config={config} />
    <MarkerSurfing config={config} />
  </>

  return <div>
    {/* <h4>Operation Mode</h4> */}
    <div>
      { config && main_tag_ready ? <Scope config={config} main_tag={main_tag} /> : null }
      {/* {followup} */}
      <pre>{JSON.stringify(cfg, null, 2)}</pre>
    </div>
  </div>
}

const Scope = ({ config, main_tag }) => {
  const media = config.doImages ? `scenes and images` : `scenes but not images`

  let tags
  if (! main_tag) {
    if (! config._vrTag)
      tags = <>no tag configured</>
  }

  return <>
    <p>
      {PLUGIN_NAME} will serve <strong>{media}</strong>
       tagged <Tag name={config._vrTag} /> <SubTags name={config._vrTag} />.
    </p>
    <p>
      Change this by changing the <em>VR Tag</em> in <Link to="/settings?tab=interface">Interface Settings</Link>.
    </p>
  </>
}

const Tag = ({ name }) => {
  const [ready, setReady] = React.useState(false)
  const [tag_id, setTagId] = React.useState(null)
  const query = `
    query Tags($name: String!) {
      findTags(tag_filter: {name: {value: $name, modifier: EQUALS}}, filter: {per_page: 1}) {
        tags {
          id
          name
        }
      }
    }`
  const get_id = useGQL(query, { name:name })

  if (ready) {
    if (tag_id)
      return <KnownTag tag_id={tag_id} name={name} />

    if (name.trim())
      return <><strong>wrong</strong> because {name} is invalid</>
    else
      return <><strong>wrong</strong> because no tag name is configured in Interface Settings</>
  }

  if (!get_id.loading && get_id.data ) {
    const found_tags = get_id.data.findTags.tags
    if (found_tags.length > 0)
      setTagId(found_tags[0].id)
    setReady(true)
  }

  // With the ID unknown, do not represent it as a valid tag yet.
  return <strong>{name}</strong>
}

const KnownTag = ({ tag_id, name }) => {
  const tag_url = `/tags/${tag_id}`
  const tagLink = <Link to={tag_url}>{name}</Link>
  return <>
    <Badge className="tag-item" pill={false} variant="secondary">{tagLink}</Badge>
  </>
}

const SubTags = ({ name }) => {
  // if (subtags)
  //   return <>
  //     or any of its <strong>{subtags.length}</strong> subtags: <SubTagsPanel subtags={subtags} />
  //   </>

  const found_subtags = {} // Map ID to name
  const scan_subtags = (children) => {
    if (children && children.length > 0) {
      for (const child of children) {
        found_subtags[child.id] = child
        scan_subtags(child.children)
      }
    }
  }

  const loading = <>(loading sub-tasks...)</>
  if (get_tags.loading || !get_tags.data)
    return loading

  const main_tag = get_tags.data.findTags.tags[0]
  if (! main_tag)
    return null

  scan_subtags(main_tag.children)
  console.log(`Found subtags:`, found_subtags)

  if (Object.keys(found_subtags).length == 0)
    return <>
      which has <strong>no sub-tags</strong>.
    </>

  const flat_subtags = Object.values(found_subtags).sort((a, b) => {
    const a_name = a.sort_name || a.name
    const b_name = b.sort_name || b.name
    return a_name.localeCompare(b_name)
  })

  console.log(`All subtags for ${main_tag.name}:`, flat_subtags)
  setSubtags(flat_subtags)
  return loading
}

const SubTagsPanel = ({ subtags }) => {
  return <div style={{marginLeft: `1em`, borderLeft: `1px solid #ccc`, paddingLeft: `1em`}}>
    {subtags.map((tag) => <KnownTag key={tag.id} tag_id={tag.id} name={tag.name} />)}
  </div>
}

const MarkerSurfing = ({ config }) => {
  return null
}

const Startup = ({ config }) => {
  const check_deps = config.skipDependencyCheck ? `will not` : `will`
  const extra = config.skipDependencyCheck
   ? `less stable but faster if ${PLUGIN_NAME} already works well and needs no updates`
   : `safer and more stable`
  return <p>
    {PLUGIN_NAME} <strong>{check_deps}</strong> check for required Python dependencies when it starts. This is {extra}.
  </p>
}

const ReadWrite = ({ config }) => {
  const label = config.readWrite ? `Read and Write` : `Read Only`
  const will = config.readWrite ? `will` : `will not`
  const change_action = config.readWrite ? `disabled` : `enabled`

  const activity_will = ( config.readWrite && config._trackActivity ) ? `will` : `will not`
  let activity_extra
  if (config.readWrite) {
    if (config._trackActivity) {
      activity_extra = <>because of <em>enabled</em></>
    } else {
      activity_extra = <>because of <em>disabled</em></>
    }
  } else {
    if (config._trackActivity) {
      activity_extra = <>despite <em>enabled</em></>
    } else {
      activity_extra = <>and note <em>disabled</em></>
    }
  }

  return <div>
    <p>
      {PLUGIN_NAME} is running in <strong>{label}</strong> mode. This means that when you use HereSphere:
    </p>
    <ul>
      <li>Clicking favorites <strong>{will}</strong> update Stash.</li>
      <li>Selecting stars <strong>{will}</strong> update Stash.</li>
      <li>Full-width HereSphere tags formatted <tt>Talent:Somebody</tt> {<strong>will</strong>} associate the performer with the scene.</li>
      <li>Other full-width HereSphere tags <strong>{will}</strong> become Stash <em>Tags</em> associated with the scene.</li>
      <li>Partial-width HereSphere tags <strong>{will}</strong> become Stash <em>Markers</em> associated with the scene.</li>
      <li>Marking a "Talent" tag 1 star <strong>{will}</strong> disassociate the performer from the scene.</li>
      <li>Marking an other tag 1 star <strong>{will}</strong> un-tag the scene in Stash.</li>
      <li>
        Viewing activity <strong>{activity_will}</strong> appear in Scene histories, {activity_extra} Scene Play History
        in <NavLink to="/settings?tab=interface">Interface Settings</NavLink>.
      </li>
    </ul>
    <p>
      Change this by setting <em>Read Write Mode</em> to <em>{change_action}</em> in the&nbsp;
      <NavLink className="nav-utility" to="/settings?tab=plugins">{PLUGIN_NAME} plugin settings</NavLink>.
    </p>
  </div>
}

const Config = ({ my_config }) => {
  // const { LoadingIndicator } = PluginApi.components

  if (!my_config)
    return <div>Loading configuration...</div>

  return <div>
    <SetDefaultConfig my_config={my_config} />
  </div>
}

const SetDefaultConfig = ({ my_config }) => {
  const [updatePluginConfig, update_query] = StashService.useConfigurePlugin()

  console.log(`Set default config, current config:`, my_config)
  if (!my_config)
    return <div>Config: not known</div>

  const new_config = get_my_config_default_updates(my_config)
  if (! new_config ) {
    console.log(`No updates needed`)
    return <div className="config" data-ok={true}></div>
  }

  // At this point, the config is known to be missing default values.
  // Set those values for better, clearer UX in the settings UI.
  console.log(`VRoom config requires updates to set default values:`, new_config)

  if ( update_query.called ) {
    const label = update_query.loading ? `updating` : `done`
    // I think the done state will not be reached because the new_config will be falsy indicating no needed changes.
    return <div>Config: {label}...</div>
  }

  // Otherwise call it
  updatePluginConfig({ variables: { plugin_id: PLUGIN_ID, input: new_config } })
  .then((result) => {
    console.log(`Plugin configuration updated`, result)
    return result
  })

  return <div>Config: updating...</div>
}

const get_my_config_default_updates = (my_config) => {
  // Return an object to update with defaults populated, or null if it is not needed.
  const update = {}

  for (const key in CONFIG_DEFAULTS) {
    const default_val = CONFIG_DEFAULTS[key]
    const current_val = my_config[key]

    // Each of these detects whether a setting which has a default is not populated (or invalid).
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

  // new_config includes all valid keyvals from the existing config.
  const new_config = {}
  for (const key in my_config)
    if (! key.startsWith("_"))
      new_config[key] = JSON.parse(JSON.stringify(my_config[key]))
  for (const key in update)
    new_config[key] = update[key]
  return new_config
}