Saved Filters
=============

Saved Filters are user-managed search queries created and edited in the
Stash web UI. When a user says "my X filter" or "the Y view", they mean
a Saved Filter.

Each mode (scenes, performers, etc.) has a list of Saved Filters. Each
Saved Filter has a unique name, unique int ID, and defines its
search, sort, and display parameters.

Commands
--------

    vroom filters                    Greppable list of all Saved Filters
    vroom filter url <mode> <ident>  Output a URL to the Saved Filter in the web UI
    vroom filter gql <mode> <ident>  Output a Saved Filter in GQL query syntax

Values:
- `mode` - scenes, images, performers, studios, tags, scene_markers, galleries, groups
- `ident` - a name, numeric ID, or `--default`

Using Saved Filters
-------------------

To use a Saved Filter via web GUI, to create links, etc, use its URL.

To run a Saved Filter as a data query, use its GQL query syntax.
(Stash stores Saved Filters in a different data shape, so `vroom` converts it.)

Default Filters
---------------

Every mode also has a "default" filter not tracked in its list.
Default filters auto-apply when navigating to a view with no query string.
The `--default` identifier will access this filter for a give mode.

Sub-Views
---------

Some Stash pages have "sub-views" which are views "within" a space
(e.g. scenes within a performer view, performers within a tag view).
Sub-views use the same Saved Filters as primary views, but keep their own distinct default filter.

Example:
- In /performers, there are saved filters, plus a default filter
- In /tags/123/performers, the same saved filters are there, but with a different default filter

Thus, these modes are also valid but only for the `--default` identifier:
- gallery_images
- group_performers
- group_scenes
- group_sub_groups
- performer_appears_with
- performer_galleries
- performer_groups
- performer_images
- performer_scenes
- studio_children
- studio_galleries
- studio_groups
- studio_images
- studio_performers
- studio_scenes
- tag_galleries
- tag_images
- tag_performers
- tag_markers
- tag_scenes

Examples
--------

```bash
vroom filter scenes --default

vroom filters | grep ^SCENES
vroom filters | grep MyFilter
vroom filter scenes "MyFilter v3"
```
