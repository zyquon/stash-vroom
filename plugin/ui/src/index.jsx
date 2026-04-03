/// <reference path="@types/pluginApi.d.ts" />
console.log(`Stash-VRoom Plugin UI start`)

const PluginApi = window.PluginApi;
const React = PluginApi.React;
const { Button } = PluginApi.libraries.Bootstrap;
const { NavLink } = PluginApi.libraries.ReactRouterDOM;
const { faVrCardboard } = PluginApi.libraries.FontAwesomeSolid;

const PATH = `/plugins/VRoom`

// import MainNavBar from "./components/MainNavBar";
import PluginHome from "./PluginHome.jsx"
import BlindInput from "./components/BlindInput/BlindInput.jsx"

export default () => {
  const { Icon } = PluginApi.components;

  // Main route: Blind input sidecar (full-screen touch surface)
  PluginApi.register.route(PATH, BlindInput)

  // Settings route: Original config page
  PluginApi.register.route(`${PATH}/settings`, PluginHome)

  PluginApi.patch.before("MainNavBar.UtilityItems", (props) => [
    {
      children: (
        <>
          <NavLink className="nav-utility" to={PATH}>
            <Button className="minimal d-flex align-items-center h-100 btn btn-primary" title="VRoom Blind Input">
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