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

    vroom filters                Greppable list of all saved filters (pipe to grep to search)
    vroom filter <mode> <name>   Show a filter as a GQL-ready query

Filter modes: scenes, images, performers, studios, tags, scene_markers, galleries

Examples
--------

```bash
vroom filters
vroom filters | grep SCENES
vroom filters | grep -i jav
vroom filter scenes "MyFilter"
```
