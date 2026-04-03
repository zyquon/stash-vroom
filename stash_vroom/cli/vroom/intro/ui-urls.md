Stash Web UI URLs
=================

When presenting query results to the user, include clickable links to
the Stash web UI so they can view or edit resources directly.

Stash web UI base URL: $STASH_BASE_URL

Detail Pages
------------

    $STASH_BASE_URL/scenes/{id}
    $STASH_BASE_URL/performers/{id}
    $STASH_BASE_URL/studios/{id}
    $STASH_BASE_URL/tags/{id}
    $STASH_BASE_URL/galleries/{id}
    $STASH_BASE_URL/images/{id}
    $STASH_BASE_URL/groups/{id}

Browse Pages
------------

Browse URLs use query parameters to encode search, sort, pagination,
and filter criteria:

    $STASH_BASE_URL/scenes?q=...&sortby=...&sortdir=...&c=...&c=...

Many of these query parameters work identically to FindFilterType in a query:

    Param   ; Description                                            ; FindFilterType field
    ------- ; ------------------------------------------------------ ; --------------------
    q       ; Search text (URI-encoded)                              ; q
    sortby  ; Sort field, e.g. "title", "date", "random_12345"       ; sort
    sortdir ; "asc" or "desc" (default: asc for most; desc for date) ; direction (ASC / DESC)
    perPage ; Items per page (default: 40)                           ; per_page
    p       ; Page number                                            ; page
    c       ; Filter criterion (repeatable, one per criterion)       ; (type-specific filter, see below)
    disp    ; Display mode (0=Grid, 1=List, 2=Wall)                  ; n/a
    z       ; Zoom index                                             ; n/a

Criterion Encoding
------------------

Each `c=` value is a JSON object with `{` and `}` replaced by `(` and `)` (but
leaving quoted strings untouched). This is Stash's custom URL encoding to
avoid curly-brace escaping in the address bar.

Encoding rules:
1. Build the criterion as JSON
2. Replace `{` with `(` and `}` with `)` (only outside quoted strings)
3. URI-encode the result (encodeURI then also encode ?#&;=+)

Example — scenes with a specific performer (ID "42"):

    JSON:  {"type":"performers","modifier":"INCLUDES_ALL","value":{"items":[{"id":"42","label":"Name"}],"excluded":[]}}
    URL c= ("type":"performers","modifier":"INCLUDES_ALL","value":("items":[("id":"42","label":"Name")],"excluded":[]))

Every criterion has `type` (the filter field name) and `modifier`
(CriterionModifier enum). The `value` shape depends on the type:

    Category     ; Value shape                                                 ; Example fields
    ------------ ; ----------------------------------------------------------- ; --------------
    String       ; "the_value"                                                 ; title, details, path
    Number/Int   ; ("value":N) or ("value":N,"value2":M) for ranges            ; rating100, duration, play_count
    Date         ; ("value":"YYYY-MM-DD") or with value2 for ranges            ; date, created_at
    ID list      ; ("items":[("id":"X","label":"L")],"excluded":[])            ; performers, galleries, groups
    Hierarchical ; ("items":[...],"excluded":[...],"depth":N)                  ; tags, studios
    Boolean      ; true                                                        ; organized, interactive

Notes:
- The `c=` value format matches the Stash UI internal format, NOT the
  GraphQL API format. Differences: UI wraps numbers in ("value":N),
  UI uses ("items":[("id":...,"label":...)] for ID lists where
  GraphQL uses plain ["id",...]. The `vroom filter` command converts
  UI format to GraphQL format.
- `label` values in ID lists are for UI display only; they do not
  affect the query. Any non-empty string works.

Full URL example — scenes rated 4+ stars, sorted by date descending, maximum zoom:

    $STASH_BASE_URL/scenes?c=("type":"rating100","modifier":"GREATER_THAN","value":("value":80))&sortby=date&sortdir=desc&z=3

Saved Filters
-------------

For Saved Filters background: `vroom intro filters`

When a user clicks a Saved Filter in the UI, Stash expands it into
the full set of query parameters and updates the URL. The URL always
contains the complete filter state.

To link a user to a Saved Filter's view: `vroom filter url <mode> <ident>`

To link to a view with its default filter applied, just link the bare
path (e.g. `$STASH_BASE_URL/scenes`) — Stash applies the default
automatically. Sub-view defaults (e.g. `performer_scenes`) are not
separately URL-addressable.

Raw access to default filter JSON:

    vroom gql '{ configuration { ui } }' | jq '.configuration.ui.defaultFilters.scenes'
    vroom gql '{ configuration { ui } }' | jq '.configuration.ui.defaultFilters.studio_scenes'

Raw access to saved filter JSON (`object_filter` is in UI format):

    vroom gql '{ findSavedFilters(mode: SCENES) { id name find_filter { q page per_page sort direction } object_filter } }'

Settings Pages
--------------

To learn about the web UI setting page, its content, and how it relates to the Stash configuration: `vroom intro ui-settings`
