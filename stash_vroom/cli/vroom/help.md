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
- Field names are often non-obvious. To see a type: `vroom schema type <Name>`
- To learn querying: `vroom intro schema`
- To learn mutations (MUST read prior to first mutation): `vroom intro mutations`

Commands
--------

Getting Data:

    vroom gql <GQL>              Execute GraphQL query argument, or `-f FILE`, or stdin `-f -`

Saved UI Filters:

    vroom filters <mode>         List user's saved search filters for "scenes", "performers", "studios", etc.
    vroom filter <mode> <name>   Show a saved filter as GQL-ready query

Miscellaneous:

    vroom version                Stash version and endpoint
    vroom config                 Stash configuration (JSON)
    vroom stats                  Database row counts

Learn More
----------

    vroom intro schema           Overview of query syntax, patterns, examples; best starting point
    vroom intro filters          How saved UI filters work, if the user mentions "filters" or "views" from the UI
    vroom intro mutations        MANDATORY prior to doing mutations: Safety guide, patterns, and examples

Quick Examples
--------------

```bash
vroom stats

vroom schema search alias
vroom schema type Performer

vroom filters scenes
vroom filter scenes "My Filter"

vroom gql '{ findScenes(filter: {per_page: 0}) { count } }'
vroom gql '{ findScenes(filter: {q: "keyword"}) { count scenes { id title } } }'
vroom gql '{ findPerformers(performer_filter: {name: {value: "Name", modifier: EQUALS}}) { performers { id name } } }'
vroom gql '{ findStudios(studio_filter: {name: {value: "Studio", modifier: EQUALS}}) { studios { id name } } }'
vroom gql '{ findTags(tag_filter: {name: {value: "^VR", modifier: MATCHES_REGEX}}) { tags { id name } } }'
```

Environment
-----------

    STASH_URL                    Stash GraphQL endpoint       $STASH_URL_STATUS
    STASH_API_KEY                API key, or reads ~/.stash/config.yml
