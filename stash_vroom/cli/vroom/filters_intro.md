Saved Filters (Views)
=====================
Saved filters are user-managed search queries created and edited in the
Stash web UI. When a user says "my X filter" or "the Y view", they mean
one of these.

Each mode (scenes, images, performers, etc.) has its own list of saved
filters, kept in alphabetical order. Filters can be referenced by their
name or numeric ID.

The Stash UI stores filters in its own internal format which differs
from the GraphQL API input types. The `vroom filter` command converts
a saved filter into GQL-ready query syntax that can be used directly
with `vroom gql`.

Commands
--------
  vroom filters <mode>            List saved filters for a mode
  vroom filter <mode> <name>      Show a filter as a GQL-ready query

Modes: scenes, images, performers, studios, tags, scene_markers, galleries

Examples
--------
  vroom filters scenes            List all saved scene filters
  vroom filters scene_markers     List all saved marker filters
  vroom filter scenes "MyFilter"  Show "MyFilter" as GQL syntax
