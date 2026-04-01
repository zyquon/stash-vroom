Data Model
----------
Scene      ->  Studio?, Performers*, Tags*, Markers*, Files* (usually 1 file)
Image      ->  Studio?, Performers*, Tags*, Files* (usually 1 file)
Performer  ->  Scenes*, Images*, Tags*; name, gender, favorite
Studio     ->  ParentStudio?, ChildStudios*, Tags*; hierarchical
Tag        ->  Parents*, Children*; hierarchical, applied to all types
Marker     ->  PrimaryTag, Tags*; timestamped bookmark in a Scene
File       ->  path, size, width, height, duration, fingerprints

Legend: ? = 0 or 1; * = 0 or more; + = 1 or more

Commands
--------

Getting Data:

  vroom gql <GQL>             Execute GraphQL query argument, or `-f FILE`, or stdin `-f -`

Saved UI Filters:

  vroom filters <mode>          List user's saved search filters
  vroom filter <mode> <name>    Show a saved filter as GQL-ready query

Valid <mode> values: scenes, images, performers, studios, tags, scene_markers. The most common is "scenes".

Miscellaneous:

  vroom version                 Stash version and endpoint
  vroom config                  Stash configuration (JSON)
  vroom stats                   Database row counts

Learn More
----------
  vroom intro schema            Overview of query syntax, patterns, examples; great starting point
  vroom intro filters           How saved UI filters (views) work
  vroom intro mutations         Safety guide, mutation patterns, and examples

Quick Examples
--------------
  vroom stats
  vroom filters scenes
  vroom filter scenes "My Filter"
  vroom gql '{ findScenes(filter: {per_page: 0}) { count } }'
  vroom gql '{ findScenes(filter: {q: "keyword"}) { count scenes { id title } } }'
  vroom gql '{ findPerformers(performer_filter: {name: {value: "Name", modifier: EQUALS}}) { performers { id name } } }'
  vroom gql '{ findStudios(studio_filter: {name: {value: "Studio", modifier: EQUALS}}) { studios { id name } } }'
  vroom gql '{ findTags(tag_filter: {name: {value: "^VR", modifier: MATCHES_REGEX}}) { tags { id name } } }'

Environment
-----------
  STASH_URL       GraphQL endpoint (default: http://127.0.0.1:9999/graphql)
  STASH_API_KEY   API key (also reads ~/.stash/config.yml)
