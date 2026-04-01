Mutations
=========

**WARNING: Mutations modify the user's database. Destructive operations
(deletes, tag overwrites, bulk updates) are irreversible. Never execute
a mutation without clearly understanding the user's intent. When in
doubt, confirm with the user before executing — especially for:**
  - **Any delete or destroy operation**
  - **Bulk updates affecting multiple items**
  - **Tag/performer ID overwrites (SET mode replaces all existing values)**
  - **Any operation the user did not explicitly request**

**Always prefer ADD/REMOVE mode over SET when modifying tags or IDs,
unless the user specifically wants to replace all values.**

Mutations are executed via `vroom gql` using GraphQL mutation syntax.
Use `vroom schema mutations` to list all 120+ available mutations, and
`vroom schema type <InputType>` to see their input fields.

Discovery:
  vroom schema mutations                         All mutation signatures
  vroom schema mutations | grep scene            Find scene-related mutations
  vroom schema mutations | grep Update           Find update mutations
  vroom schema type SceneUpdateInput             See input fields for scene update

Common mutation patterns:

```bash
# Update a scene's title
vroom gql 'mutation { sceneUpdate(input: {id: "123", title: "New Title"}) { id title } }'

# Update a scene's rating (0-100 scale)
vroom gql 'mutation { sceneUpdate(input: {id: "123", rating100: 80}) { id rating100 } }'

# Set tags on a scene (full replacement — overwrites all existing tags)
vroom gql 'mutation { sceneUpdate(input: {id: "123", tag_ids: ["10", "20"]}) { id tags { name } } }'

# Update a performer
vroom gql 'mutation { performerUpdate(input: {id: "456", favorite: true}) { id name favorite } }'
```

Notes:
- Mutations return the updated object — request the fields you want to verify
- sceneUpdate's tag_ids, performer_ids, etc. are full replacements, not additions

Updating tags (and performer_ids, studio_id, etc.) without full replacement:
  bulkSceneUpdate accepts tag_ids as BulkUpdateIds: {ids: [...], mode: MODE}

  Modes (BulkUpdateIdMode):
    SET      Replace all (same as sceneUpdate's tag_ids)
    ADD      Add to existing, keep the rest
    REMOVE   Remove specific, keep the rest

```bash
# Add a tag to a scene without affecting existing tags
vroom gql 'mutation { bulkSceneUpdate(input: {ids: ["123"], tag_ids: {ids: ["10"], mode: ADD}}) { id tags { name } } }'

# Remove a tag from a scene
vroom gql 'mutation { bulkSceneUpdate(input: {ids: ["123"], tag_ids: {ids: ["10"], mode: REMOVE}}) { id tags { name } } }'

# Add a tag to multiple scenes at once
vroom gql 'mutation { bulkSceneUpdate(input: {ids: ["123", "456", "789"], tag_ids: {ids: ["10"], mode: ADD}}) { id tags { name } } }'
```

The same BulkUpdateIds pattern works for performer_ids, gallery_ids, etc.
on bulkSceneUpdate, bulkImageUpdate, bulkPerformerUpdate, etc.
