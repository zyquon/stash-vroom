/// <reference path="@types/pluginApi.d.ts" />
console.log(`Stash-VRoom Plugin UI start`)

const PluginApi = window.PluginApi;
const React = PluginApi.React;
const { Button } = PluginApi.libraries.Bootstrap;
const { NavLink } = PluginApi.libraries.ReactRouterDOM;
const { faVrCardboard } = PluginApi.libraries.FontAwesomeSolid;

const STATIC_AND_REACT_PATH = `/plugin/VRoom/assets/static/VRoom.html`;

// import MainNavBar from "./components/MainNavBar";
import PluginHome from "./PluginHome.jsx"

const Bounce = (props) => {
  const { useHistory } = PluginApi.libraries.ReactRouterDOM
  const history = useHistory();
  history.push(props.to)
  return null
}

export default () => {
  const { Icon } = PluginApi.components;

  PluginApi.register.route(STATIC_AND_REACT_PATH, PluginHome)

  PluginApi.patch.instead('App', (props, _, Original) => {
    const match = (window.location.hash || "").match(/^#(\/.*)$/)
    if (match) {
      const new_path = match[1];
      console.log(`Redirect from hash: ${window.location.hash} to path: ${new_path}`);
      return <Bounce to={new_path} />
    }

    return [ <Original {...props} /> ]
  })

  PluginApi.patch.before("MainNavBar.UtilityItems", (props) => [
    {
      children: (
        <>
          <NavLink className="nav-utility" to={STATIC_AND_REACT_PATH}>
            <Button className="minimal d-flex align-items-center h-100 btn btn-primary" title="VRoom hello world tooltip?">
              <Icon icon={faVrCardboard} />
            </Button>
          </NavLink>
          {props.children}
        </>
      ),
    }
  ])
}

// To obtain type support for PluginApi.libraries, simply install its respective "@types/library" or the library itself.
// These libraries will not be bundled, as stash-plugin-builder will automatically maps them to PluginApi.libraries.