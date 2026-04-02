Querying Stash
==============

Queries
-------

These are the most common queries.
All find* queries follow the same pattern with two filter arguments:

    findScenes(filter, scene_filter)              -> count, scenes
    findImages(filter, image_filter)              -> count, images
    findPerformers(filter, performer_filter)      -> count, performers
    findStudios(filter, studio_filter)            -> count, studios
    findTags(filter, tag_filter)                  -> count, tags
    findSceneMarkers(filter, scene_marker_filter) -> count, scene_markers

Use `vroom schema queries` for the full list with signatures.

Pagination and Sorting
----------------------

The common `filter` argument (`FindFilterType`) controls pagination and sorting:

    q          String    Text search, detailed below
    page       Int       Page number, default 1
    per_page   Int       Results per page, default 25, 0 means count only (no items), -1 means no limit
    sort       String    Field name (e.g. "title", "date", "random")
    direction  Enum      ASC | DESC, default is ASC

### Text search

The `q` field supports boolean logic, negation, and exact phrases.
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

```bash
vroom gql '{ findScenes(filter: {q: "poolside -amateur"}) { count scenes { id title } } }'
vroom gql '{ findPerformers(filter: {q: "alice OR bob"}) { performers { id name } } }'
```

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

CriterionModifier Values
-------------------------

    EQUALS, NOT_EQUALS           Exact match / exclusion
    GREATER_THAN, LESS_THAN      Numeric comparison
    IS_NULL, NOT_NULL            Existence check
    INCLUDES, INCLUDES_ALL       ID list: any match / all must match
    EXCLUDES                     ID list: none may match
    MATCHES_REGEX                Go RE2 match; prefix (?i) for case-insensitive
    NOT_MATCHES_REGEX            Go RE2 exclusion
    BETWEEN, NOT_BETWEEN         Range (use value + value2)

Hierarchical Filters (Tags, Studios)
-------------------------------------

Tags and Studios are hierarchical. Optionally filter with a depth limit to handle descendants:

    {value: ["TAG_ID"], modifier: INCLUDES_ALL, depth: N}

    depth: 0   Match the exact tag only (default)
    depth: 1   Include direct children
    depth: -1  Include all descendants

Tips
----

### Field names are non-obvious

Stash field names often differ from what you'd guess. Discover fields rather than guess:

```bash
vroom schema type --multi Performer Scene
```

### Pre-fetch IDs you will need

Filtering by Studio, Performer, or Tag requires their IDs. Use a two-step pattern: first find the ID by name, then filter by ID:

```bash
# Step 1: Find studio ID
vroom gql '{ findStudios(studio_filter: {name: {value: "StudioName", modifier: EQUALS}}) { studios { id name } } }'

# Step 2: Use ID to find scenes
vroom gql '{ findScenes(scene_filter: {studios: {value: ["STUDIO_ID"], modifier: INCLUDES}}) { count scenes { id title } } }'
```

### Important Conventions

    rating100       Ratings are 0-100, not 0-5 (20 = 1 star, 100 = 5 stars)
    sort: "random"  Random sort; Stash appends a seed, e.g. "random_12345"
    has_markers     String, not boolean: "true" or "false"
    is_missing      String field name: e.g. "stash_id", "studio", "performers"
    alias_list      Performer aliases field is "alias_list", not "aliases"

Mutations
---------

Before the first mutation, read the MANDATORY mutation guide:

```bash
vroom intro mutations
```

Then, list or grep for supported mutations:

```
$ vroom schema mutations | grep ^stop
stopAllJobs: Boolean!
stopJob(job_id: ID!): Boolean!
```

Schema Discovery
================

Now that you know how to query, you must discover the relevant types and data schemas.
These commands help you find what you need:

    vroom schema queries            List all query signatures, alphabetical, one per line
    vroom schema mutations          List all mutation signatures, alphabetical, one per line
    vroom schema types              List all types, alphabetical, one per line
    vroom schema search <term>      Search across types, fields, enums
    vroom schema type <TypeName>    List fields of a specific type, one per line

Output: queries and mutations
-----------------------------

Both `vroom schema queries` and `vroom schema mutations` output a flat list of signatures:

```
$ vroom schema queries | grep '^findTag('
findTag(id: ID!): Tag

$ vroom schema mutations | grep ^imageResetO
imageResetO(id: ID!): Int!
```

Output: types
-------------

`vroom schema types` is formatted one type per line, either 2-column "KIND ; TypeName" or 3-column "KIND ; TypeName ; Description if present". Padding aligns the columns. Example of each kind:

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

# Substring match
vroom schema types | grep ^OBJECT | grep Performer

# Prefix match
vroom schema types | grep ^OBJECT | grep '; Performer'

# Exact match
vroom schema types | grep ^OBJECT | grep '; Performer\b'
```

Output: search
--------------

`vroom schema search` results are grouped into matching types, fields, and enums.

```
$ vroom schema search loglevel
Types matching 'loglevel':
  ENUM           LogLevel

Fields matching 'loglevel':
  ConfigGeneralInput.logLevel: String
  ConfigGeneralResult.logLevel: String!
```

Output: specific type schema
----------------------------

`vroom schema type` is the key command to see a type schema. Lines are formatted with the familiar greppable 2-or-3 column layout: field name, its type, description (if present).

```
$ vroom schema type Scene | grep Time
created_at     ; Time!
updated_at     ; Time!
last_played_at ; Time     ; The last time play count was updated
play_history   ; [Time!]! ; Times a scene was played
o_history      ; [Time!]! ; Times the o counter was incremented
```

To look up multiple types in one call, use `--multi` which will show types grouped, with clear headers.

```
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
