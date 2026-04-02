Data Model
----------

Scene       ->  Studio?, Performers*, Tags*, Markers*, VideoFiles* (usually 1 file)
Performer   ->  Scenes*, Images*, Tags*; name, gender, favorite
Studio      ->  ParentStudio?, ChildStudios*, Tags*; hierarchical
Tag         ->  Parents*, Children*; hierarchical, applied to all types
SceneMarker ->  PrimaryTag, Tags*; timestamped bookmark in a Scene
VideoFile   ->  path, basename, size, width, height, duration

Legend: ? = 0 or 1; * = 0 or more; + = 1 or more

Notes:
- To learn querying: `vroom intro queries`
- Field names are often non-obvious. To see a type: `vroom schema type <Name>`
- To learn mutations (MUST read prior to first mutation): `vroom intro mutations`

Commands
--------

Using Data:

    vroom gql <GQL>              Execute GraphQL argument, or `-f FILE`, or stdin `-f -`

Saved UI Filters:

    vroom filters                Greppable list of saved searches used by the web UI
    vroom filter <mode> <name>   Show a saved filter as GQL-ready query

Maintenance and Troubleshooting:

    vroom version                Stash version and endpoint
    vroom config                 Stash configuration (JSON)
    vroom stats                  Database row counts
    vroom logs                   Greppable list of recent (~30) log entries

Learn More
----------

    vroom intro queries          Query syntax, patterns, and examples; best starting point
    vroom intro discovery        Schema discovery: finding types, fields, queries, mutations
    vroom intro filters          How saved UI filters work, if the user mentions UI "filters", "bookmarks", "views", etc.
    vroom intro mutations        MANDATORY prior to doing mutations: Safety guide, patterns, and examples
    vroom intro ui-urls          Advice for generating Stash web UI URLs to objects, UI filters, views, etc.

Quick Examples
--------------

```bash
vroom stats
vroom logs | grep -E '^(Warning|Error)'

vroom schema search alias
vroom schema type Performer

vroom filters | grep ^SCENES
vroom filter SCENES "My Filter"

vroom gql '{ findScenes(filter: {per_page: 0}) { count } }'
vroom gql '{ findScenes(filter: {q: "keyword"}) { count scenes { id title } } }'
vroom gql '{ findPerformers(performer_filter: {name: {value: "Name", modifier: EQUALS}}) { performers { id name } } }'
vroom gql '{ findStudios(studio_filter: {name: {value: "Studio", modifier: EQUALS}}) { studios { id name } } }'
vroom gql '{ findTags(tag_filter: {name: {value: "^VR", modifier: MATCHES_REGEX}}) { tags { id name } } }'
```

Environment
-----------

    STASH_URL                    Stash GraphQL endpoint       $STASH_URL_STATUS
    STASH_HOME                   Stash config directory       $STASH_HOME_STATUS
    STASH_API_KEY                API key                      $STASH_API_KEY_STATUS
