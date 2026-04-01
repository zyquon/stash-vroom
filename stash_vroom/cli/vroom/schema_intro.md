GraphQL Query Patterns
======================

Queries
-------
All find* queries follow the same pattern with two filter arguments:

  findScenes(filter, scene_filter)              -> count, scenes
  findImages(filter, image_filter)              -> count, images
  findPerformers(filter, performer_filter)      -> count, performers
  findStudios(filter, studio_filter)            -> count, studios
  findTags(filter, tag_filter)                  -> count, tags
  findSceneMarkers(filter, scene_marker_filter) -> count, scene_markers
  findSavedFilters(mode)                        -> saved user searches

Use `vroom schema queries` for the full list with signatures.

Pagination and Sorting: FindFilterType
--------------------------------------
The `filter` argument controls pagination and sorting:

  q          String    Text search, detailed below
  page       Int       Page number, default 1
  per_page   Int       Results per page, default 25, 0 means count only (no items), -1 means no limit
  sort       String    Field name (e.g. "title", "date", "random")
  direction  Enum      ASC | DESC, default is ASC

Search Syntax (the q field)
---------------------------
The q field supports boolean logic, negation, and exact phrases.
It is case-insensitive and matches against type-specific fields:

  Scenes:     title, details, path, oshash, checksum, marker titles
  Images:     title, path, checksum
  Performers: name, aliases
  Studios:    name, aliases
  Tags:       name, aliases
  Markers:    title, scene title
  Galleries:  title, path, checksum

Syntax:
  foo bar           AND: both words must match (default)
  foo OR bar        OR: either word matches (also: foo | bar)
  -bar              NOT: exclude matches containing "bar"
  "foo bar"         Exact phrase match (preserves spaces)
  -"foo bar"        Exclude exact phrase
  "OR"              Literal OR (quoting escapes keywords)
  "-bar"            Literal -bar (quoting escapes negation)
  %                 Wildcard: zero or more characters
  _                 Wildcard: exactly one character

OR groups combine with AND:
  foo OR bar baz    Matches (foo OR bar) AND baz

Wildcard examples:
  2026-03-%.mp4     Matches all March 2026 ending in .mp4
  scene-2_          Matches "scene-2A", "scene-25"

CLI examples:
  vroom gql '{ findScenes(filter: {q: "poolside -amateur"}) { count scenes { id title } } }'
  vroom gql '{ findPerformers(filter: {q: "alice OR bob"}) { performers { id name } } }'

Type-Specific Filters
---------------------
The second argument (scene_filter, image_filter, etc.) is type-specific.
Use `vroom schema type <TheFilterType>` to see any of: SceneFilterType, ImageFilterType, PerformerFilterType, StudioFilterType, TagFilterType, SceneMarkerFilterType

Filter fields use typed criteria:

  String fields:    {value: "...",  modifier: EQUALS}
  ID list fields:   {value: ["id"], modifier: INCLUDES}
  Int fields:       {value: N,      modifier: GREATER_THAN}
  Boolean fields:   true or false directly (no modifier)
  Composable:       AND, OR, NOT (each nests another FilterType)

Two-Step ID Lookup
------------------
Filtering by Studio, Performer, or Tag requires their IDs. Use a two-step
pattern: first find the ID by name, then filter by it. Example:

```bash
# Step 1: Find studio ID
vroom gql '{ findStudios(studio_filter: {name: {value: "StudioName", modifier: EQUALS}}) { studios { id name } } }'

# Step 2: Use ID to find scenes
vroom gql '{ findScenes(scene_filter: {studios: {value: ["STUDIO_ID"], modifier: INCLUDES}}) { count scenes { id title } } }'
```

Important Conventions
---------------------
  rating100       Ratings are 0-100, not 0-5 (20 = 1 star, 100 = 5 stars)
  sort: "random"  Random sort; Stash appends a seed, e.g. "random_12345"
  has_markers     String, not boolean: "true" or "false"
  is_missing      String field name: e.g. "stash_id", "studio", "performers"

CriterionModifier Values
-------------------------
  EQUALS, NOT_EQUALS           Exact match / exclusion
  GREATER_THAN, LESS_THAN      Numeric comparison
  IS_NULL, NOT_NULL            Existence check
  INCLUDES, INCLUDES_ALL       ID list: any match / all must match
  EXCLUDES                     ID list: none may match
  MATCHES_REGEX                Regex match on strings
  NOT_MATCHES_REGEX            Regex exclusion
  BETWEEN, NOT_BETWEEN         Range (use value + value2)

Hierarchical Filters (Tags, Studios)
-------------------------------------
Tags and Studios are hierarchical. Optionally filter with a depth limit to handle descendants:

  {value: ["TAG_ID"], modifier: INCLUDES_ALL, depth: N}

  depth: 0   Match the exact tag only (default)
  depth: 1   Include direct children
  depth: -1  Include all descendants

Mutations
---------
Before running any mutation, read the mutation guide first:

  vroom intro mutations             Safety guidelines, patterns, and examples
  vroom schema mutations            List all mutation signatures

Schema Discovery
----------------
Use vroom to discover data schemas. These commands help you find what you need:

  vroom schema types              All types, alphabetical, one per line
  vroom schema queries            All query signatures, alphabetical, one per line
  vroom schema search <term>      Search across types, fields, enums
  vroom schema type <TypeName>    List fields of a specific type, one per line

Often you first use `queries`, `types`, and/or `search` to know what types to use, followed by `type TypeName` to get specific type schemas.

### Schema types output

`vroom schema types` is formatted either 2-column "KIND ; TypeName" or 3-column "KIND ; TypeName ; Description if present". Padding aligns the columns. Example of each kind:

    ENUM         ; LogLevel
    INPUT_OBJECT ; StashConfigInput ; Stash configuration details
    INTERFACE    ; BaseFile
    OBJECT       ; ConfigResult     ; All configuration settings
    SCALAR       ; Int64
    UNION        ; VisualFile

There are about 300 total types. Use `grep` to find what you need:

```bash
# Filter by kind
vroom schema types | grep ^SCALAR

# Type substring match
vroom schema types | grep ^OBJECT | grep Performer

# Type prefix match
vroom schema types | grep ^OBJECT | grep '; Performer'

# Type suffix match
vroom schema types | grep ^OBJECT | grep 'Result\b'

# Type exact match
vroom schema types | grep ^OBJECT | grep '; Performer\b'
```

### Schema queries output

Queries are a flat list of queries with signatures. Example interaction:

```bash
# Exact match
$ vroom schema queries | grep '^findTag('
findTag(id: ID!): Tag
```

### Schema search output

Search results are grouped into sections by type. Example interaction:

```bash
$ vroom schema search loglevel
Types matching 'loglevel':
  ENUM           LogLevel

Fields matching 'loglevel':
  ConfigGeneralInput.logLevel: String
  ConfigGeneralResult.logLevel: String!
```

### Schema type output

This is the key command to see a type schema. Lines are formatted with the familiar greppable 2-or-3 column layout: field name, its type, description (if present).

Example interaction (edited for brevity):

```bash
# Show only scene fields using the Time type
$ vroom schema type Scene | grep Time
created_at     ; Time!
updated_at     ; Time!
last_played_at ; Time     ; The last time play count was updated
play_history   ; [Time!]! ; Times a scene was played
o_history      ; [Time!]! ; Times the o counter was incremented

# See multiple types at once; --multi formats the output
$ vroom schema type --multi Performer Scene VideoFile Tag
Performer
---------
id   ; ID!
name ; String!
[...snip...]

Scene
-----
id    ; ID!
title ; String
[...snip...]

VideoFile
---------
id   ; ID!
path ; String!
[...snip...]

Tag
---
id   ; ID!
name ; String!
[...snip...]
```
