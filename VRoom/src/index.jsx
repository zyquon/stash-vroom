/// <reference path="@types/pluginApi.d.ts" />

import Button from "./components/Button/Button"

export default () => {
  console.log(Button())
}

// To obtain type support for PluginApi.libraries, simply install its respective "@types/library" or the library itself.
// These libraries will not be bundled, as stash-plugin-builder will automatically maps them to PluginApi.libraries.
