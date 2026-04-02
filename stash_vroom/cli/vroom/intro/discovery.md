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
