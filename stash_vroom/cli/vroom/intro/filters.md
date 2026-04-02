Saved Filters (Views)
=====================

Saved filters are user-managed search queries created and edited in the
Stash web UI. When a user says "my X filter" or "the Y view", they mean
one of these.

Each mode (scenes, images, performers, etc.) has its own alphabetical
list of saved filters, referenced by name or numeric ID.

The Stash UI stores filters in its own internal format which differs
from the GraphQL API input types. The `vroom filter` command converts
a saved filter into GQL-ready query syntax that can be used directly
with `vroom gql`.

Commands
--------

    vroom filters                    Greppable list of all saved filters (pipe to grep to search)
    vroom filter <mode> <name>       Show a filter as a GQL-ready query
    vroom filter <mode> --default    Show the default filter for a mode

Filter modes: scenes, images, performers, studios, tags, scene_markers, galleries

Default filters are configured per-view in the Stash UI and auto-apply
when navigating to that view with no query string. They are stored in
the UI config blob, not in the saved filters list, so `vroom filters`
will not show them. Use `--default` to retrieve them.

Examples
--------

```bash
vroom filters
vroom filters | grep ^SCENES
vroom filters | grep -i jav
vroom filter scenes "MyFilter"
vroom filter scenes --default
vroom filter performers --default
```
