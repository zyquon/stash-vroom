Data Model
----------

Scene       ->  Studio?, Performers*, Tags*, Markers*, VideoFiles* (usually 1 file)
Performer   ->  Scenes*, Images*, Tags*; name, gender, favorite
Studio      ->  ParentStudio?, ChildStudios*, Tags*; hierarchical
Tag         ->  Parents*, Children*; hierarchical, applied to all types
SceneMarker ->  PrimaryTag, Tags*; timestamped bookmark in a Scene
VideoFile   ->  path, basename, size, width, height, duration

Legend: ? = 0 or 1; * = 0 or more; + = 1 or more

Commands
--------

Start Here:

    vroom intro queries          FIRST READ: Query syntax, patterns, examples
    vroom gql <GQL>              Execute a query, or `-f FILE`, or stdin `-f -`

`vroom gql` outputs the GraphQL `data` value, unwrapped from its envelope (or an error message).

Learn More (as needed):

    vroom intro discovery        Schema discovery: finding types, fields, queries, mutations
    vroom intro filters          Saved Filters: the user's quick-access queries (AKA views, bookmarks, etc.), for the web UI
    vroom intro mutations        MANDATORY prior to doing mutations: Safety guide, patterns, and examples
    vroom intro ui-urls          Advice for generating Stash web UI URLs to objects, UI filters, views, etc.

Maintenance and Troubleshooting:

    vroom version                Stash version and endpoint
    vroom config                 Stash configuration (JSON)
    vroom stats                  Database row counts
    vroom logs                   Greppable list of recent (~30) log entries

Quick Examples
--------------

```bash
vroom stats
vroom logs | grep -E '^(Warning|Error)'

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
