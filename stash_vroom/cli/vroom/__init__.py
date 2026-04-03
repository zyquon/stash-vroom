#!/usr/bin/env python3
"""vroom - Stash database explorer

A CLI tool to interface with the Stash (AKA StashApp) media organizer.
`vroom` exposes the Stash GraphQL API, for queries and exploration.
"""

import argparse
import importlib.resources
import json
import os
import signal
import string
import sys
import httpx


import stash_vroom.stash

DEFAULT_STASH_SERVER = f'http://localhost:9999'
DEFAULT_STASH_ENDPOINT = f'{DEFAULT_STASH_SERVER}/graphql'

def _read_doc(name, context=None):
    """Read a bundled text file from this package, with $variable substitution."""
    text = importlib.resources.files(__package__).joinpath(name).read_text(encoding='utf-8')

    if not context:
        context = _default_docs_context()

    text = string.Template(text).safe_substitute(context)
    return text


def _default_docs_context():
    """Build template context for bundled docs."""
    result = {}

    stash_url = os.environ.get('STASH_URL')
    result['STASH_URL_STATUS'] = stash_url if stash_url else f'Unset, default is {DEFAULT_STASH_ENDPOINT}'

    stash_home = os.environ.get('STASH_HOME')
    result['STASH_HOME_STATUS'] = stash_home if stash_home else f'Unset, default is {stash_vroom.stash.STASH_HOME}'

    # Base URL for web UI links (GraphQL endpoint minus /graphql suffix)
    gql_url = stash_url or DEFAULT_STASH_ENDPOINT
    result['STASH_BASE_URL'] = gql_url.removesuffix('/graphql')

    api_key = os.environ.get('STASH_API_KEY')
    if api_key:
        result['STASH_API_KEY_STATUS'] = 'Set'
    else:
        api_key = stash_vroom.stash.get_api_key()
        if api_key:
            result['STASH_API_KEY_STATUS'] = f'Unset, using {stash_vroom.stash.STASH_HOME}/config.yml'
        else:
            result['STASH_API_KEY_STATUS'] = f'Unset and no config found!'

    return result


# ---------------------------------------------------------------------------
# Introspection query constants
# ---------------------------------------------------------------------------

INTROSPECT_TYPES_LIST = """
{
  __schema {
    types {
      name
      kind
      description
    }
  }
}
"""

INTROSPECT_TYPE_DETAIL = """
query IntrospectType($name: String!) {
  __type(name: $name) {
    name
    kind
    description
    fields {
      name
      description
      type { ...TypeRef }
      args {
        name
        type { ...TypeRef }
        defaultValue
      }
    }
    inputFields {
      name
      description
      type { ...TypeRef }
      defaultValue
    }
    enumValues {
      name
      description
    }
  }
}

fragment TypeRef on __Type {
  name kind
  ofType {
    name kind
    ofType {
      name kind
      ofType {
        name kind
        ofType { name kind }
      }
    }
  }
}
"""

# Full introspection for search (single round trip)
INTROSPECT_FULL = """
{
  __schema {
    types {
      name
      kind
      description
      fields {
        name
        description
        type {
          name kind
          ofType { name kind ofType { name kind ofType { name kind } } }
        }
      }
      inputFields {
        name
        description
        type {
          name kind
          ofType { name kind ofType { name kind ofType { name kind } } }
        }
      }
      enumValues {
        name
        description
      }
    }
  }
}
"""

INTROSPECT_ROOT = """
{
  __schema {
    queryType { name }
    mutationType { name }
  }
}
"""


# ---------------------------------------------------------------------------
# Connection and GraphQL helpers
# ---------------------------------------------------------------------------

def get_connection(args):
    """Return (url, headers) for Stash API."""
    url = getattr(args, 'url', None) or os.environ.get('STASH_URL', DEFAULT_STASH_ENDPOINT)
    api_key = stash_vroom.stash.get_api_key()
    headers = {'ApiKey': api_key, 'Content-Type': 'application/json'}
    return url, headers


def gql(url, headers, query, variables=None):
    """Execute a GraphQL query and return the data dict."""
    payload = {'query': query}
    if variables:
        payload['variables'] = variables
    resp = httpx.post(url, json=payload, headers=headers, timeout=30)
    try:
        body = resp.json()
    except Exception:
        resp.raise_for_status()
        raise
    if 'errors' in body:
        for err in body['errors']:
            print(f"GraphQL error: {err.get('message', err)}", file=sys.stderr)
        if 'data' not in body or body['data'] is None:
            sys.exit(1)
    if not resp.is_success:
        print(f"HTTP {resp.status_code}", file=sys.stderr)
        sys.exit(1)
    return body.get('data')


def render_type_ref(t):
    """Render a GraphQL type reference like [Scene!]! from introspection."""
    if t is None:
        return '?'
    kind = t.get('kind')
    if kind == 'NON_NULL':
        return f'{render_type_ref(t.get("ofType"))}!'
    if kind == 'LIST':
        return f'[{render_type_ref(t.get("ofType"))}]'
    return t.get('name') or '?'


def format_columns(rows, sep=';'):
    """Format rows into aligned columns separated by a delimiter.

    Each row is a list of values. Trailing None/empty values are omitted
    along with their separator, so no trailing whitespace or delimiters appear.
    Columns are right-padded only when a subsequent column exists on that row.
    """
    # Determine max width per column (only counting rows that have content beyond that column)
    col_count = max((len(r) for r in rows), default=0)
    max_widths = [0] * col_count
    for row in rows:
        # Find last non-empty column in this row
        last = len(row) - 1
        while last >= 0 and not row[last]:
            last -= 1
        # Only columns before `last` need padding
        for i in range(last):
            max_widths[i] = max(max_widths[i], len(str(row[i])))

    lines = []
    for row in rows:
        # Find last non-empty column
        last = len(row) - 1
        while last >= 0 and not row[last]:
            last -= 1
        if last < 0:
            lines.append('')
            continue
        parts = []
        for i in range(last + 1):
            val = str(row[i]) if i < len(row) else ''
            if i < last:
                parts.append(f'{val:<{max_widths[i]}}')
            else:
                parts.append(val)
        lines.append(f' {sep} '.join(parts))
    return '\n'.join(lines)


def strip_nulls(obj):
    """Remove null values from a dict/list tree for compact output."""
    if isinstance(obj, dict):
        return {k: strip_nulls(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [strip_nulls(v) for v in obj]
    return obj


def json_out(data, compact=False):
    """Print JSON, optionally compact (no nulls)."""
    if compact:
        data = strip_nulls(data)
    print(json.dumps(data, indent=2))


# ---------------------------------------------------------------------------
# Command: logs
# ---------------------------------------------------------------------------

def cmd_logs(args):
    url, headers = get_connection(args)
    data = gql(url, headers, '{ logs { time level message } }')
    entries = data.get('logs') or []

    rows = []
    for e in entries:
        rows.append([e['level'], e['time'], e['message']])
    print(format_columns(rows))


# ---------------------------------------------------------------------------
# Command: version
# ---------------------------------------------------------------------------

def cmd_version(args):
    url, headers = get_connection(args)
    data = gql(url, headers, '{ version { version hash build_time } }')
    v = data['version']
    print(f"Stash {v['version']} (build {v['build_time']}, hash {v['hash'][:8]})")
    print(f"Endpoint: {url}")


# ---------------------------------------------------------------------------
# Command: config
# ---------------------------------------------------------------------------

def cmd_config(args):
    url, headers = get_connection(args)
    query = """
    {
      configuration {
        general {
          stashes { path excludeVideo excludeImage }
          databasePath
          generatedPath
          metadataPath
          cachePath
          calculateMD5
          videoFileNamingAlgorithm
          parallelTasks
          previewSegments
          previewSegmentDuration
          previewExcludeStart
          previewExcludeEnd
          previewPreset
          maxTranscodeSize
          maxStreamingTranscodeSize
          apiKey
          username
          ffmpegPath
          ffprobePath
          logLevel
          logAccess
          logOut
          stashBoxes { name endpoint }
        }
        defaults {
          scan {
            scanGenerateCovers
            scanGeneratePreviews
            scanGenerateImagePreviews
            scanGenerateSprites
            scanGeneratePhashes
            scanGenerateThumbnails
          }
        }
      }
    }
    """
    data = gql(url, headers, query)
    config = data['configuration']

    # Redact secrets
    general = config.get('general', {})
    if general.get('apiKey'):
        general['apiKey'] = '***'

    json_out(config, compact=True)


# ---------------------------------------------------------------------------
# Command: stats
# ---------------------------------------------------------------------------

def cmd_stats(args):
    url, headers = get_connection(args)
    query = """
    {
      findScenes(filter:{per_page:0}) { count }
      findImages(filter:{per_page:0}) { count }
      findPerformers(filter:{per_page:0}) { count }
      findStudios(filter:{per_page:0}) { count }
      findTags(filter:{per_page:0}) { count }
      findSceneMarkers(filter:{per_page:0}) { count }
      findGalleries(filter:{per_page:0}) { count }
    }
    """
    data = gql(url, headers, query)
    stats = [
        ('Scenes',     data['findScenes']['count']),
        ('Images',     data['findImages']['count']),
        ('Performers', data['findPerformers']['count']),
        ('Studios',    data['findStudios']['count']),
        ('Tags',       data['findTags']['count']),
        ('Markers',    data['findSceneMarkers']['count']),
        ('Galleries',  data['findGalleries']['count']),
    ]
    w = max(len(s[0]) for s in stats)
    for name, count in stats:
        print(f"  {name:<{w}}  {count:>8,}")


# ---------------------------------------------------------------------------
# Command: query
# ---------------------------------------------------------------------------

def cmd_gql(args):
    url, headers = get_connection(args)

    if args.file:
        if args.file == '-':
            query_str = sys.stdin.read()
        else:
            with open(args.file) as f:
                query_str = f.read()
    elif args.query:
        query_str = args.query
    elif not sys.stdin.isatty():
        query_str = sys.stdin.read()
    else:
        print("Provide a GraphQL query string, -f FILE, or pipe to stdin", file=sys.stderr)
        sys.exit(1)

    variables = None
    if args.variables:
        variables = json.loads(args.variables)

    data = gql(url, headers, query_str, variables)
    json_out(data, compact=True)




# ---------------------------------------------------------------------------
# Command: filters
# ---------------------------------------------------------------------------

FILTER_MODES = [
    'SCENES', 'IMAGES', 'PERFORMERS', 'STUDIOS',
    'TAGS', 'SCENE_MARKERS', 'GALLERIES', 'MOVIES', 'GROUPS',
]

# Sub-view modes: only valid with --default (they have default filters but
# no saved filter lists of their own).
SUBVIEW_MODES = [
    'GALLERY_IMAGES',
    'GROUP_PERFORMERS', 'GROUP_SCENES', 'GROUP_SUB_GROUPS',
    'PERFORMER_APPEARS_WITH', 'PERFORMER_GALLERIES', 'PERFORMER_GROUPS',
    'PERFORMER_IMAGES', 'PERFORMER_SCENES',
    'STUDIO_CHILDREN', 'STUDIO_GALLERIES', 'STUDIO_GROUPS',
    'STUDIO_IMAGES', 'STUDIO_PERFORMERS', 'STUDIO_SCENES',
    'TAG_GALLERIES', 'TAG_IMAGES', 'TAG_PERFORMERS',
    'TAG_MARKERS', 'TAG_SCENES',
]


def _resolve_filter_mode(args):
    """Resolve and validate filter mode from args."""
    mode = args.mode.upper()
    is_default = getattr(args, 'default', False)

    if mode in FILTER_MODES:
        return mode
    if mode in SUBVIEW_MODES:
        if not is_default:
            print(f"Sub-view mode '{mode.lower()}' is only valid with --default", file=sys.stderr)
            sys.exit(1)
        return mode

    all_modes = FILTER_MODES + (SUBVIEW_MODES if is_default else [])
    print(f"Invalid mode: {mode}", file=sys.stderr)
    print(f"Valid modes: {', '.join(all_modes)}", file=sys.stderr)
    sys.exit(1)


def cmd_intro(args):
    topic = args.topic
    if not topic:
        print(_read_doc('help.md'), end='')
        return
    topics = {
        'queries': 'intro/queries.md',
        'discovery': 'intro/discovery.md',
        'filters': 'intro/filters.md',
        'mutations': 'intro/mutations.md',
        'ui-urls': 'intro/ui-urls.md',
        'ui-settings': 'intro/ui-settings.md',
    }
    if topic not in topics:
        print(f"Unknown topic: {topic}", file=sys.stderr)
        print(f"Available topics: {', '.join(topics)}", file=sys.stderr)
        sys.exit(1)
    print(_read_doc(topics[topic]), end='')


def cmd_filters(args):
    url, headers = get_connection(args)

    query = """
    query($mode: FilterMode!) {
      findSavedFilters(mode: $mode) {
        id mode name
      }
    }
    """
    rows = []
    for mode in FILTER_MODES:
        data = gql(url, headers, query, {'mode': mode})
        for f in data['findSavedFilters']:
            rows.append([mode, str(f['id']), f['name']])

    print(format_columns(rows))


# ---------------------------------------------------------------------------
# Command: filter (show or run)
# ---------------------------------------------------------------------------

def _fetch_default_filter(url, headers, mode):
    """Fetch the default filter for a mode from the UI config blob."""
    data = gql(url, headers, '{ configuration { ui } }')
    ui = data.get('configuration', {}).get('ui') or {}
    defaults = ui.get('defaultFilters') or {}
    key = mode.lower()
    found = defaults.get(key)
    if not found:
        print(f"No default filter for mode: {key}", file=sys.stderr)
        sys.exit(1)
    return found


def _fetch_saved_filter(url, headers, mode, args):
    """Fetch a saved or default filter. Returns (found, is_default)."""
    if getattr(args, 'default', False):
        return _fetch_default_filter(url, headers, mode), True

    name_or_id = args.name
    if not name_or_id:
        print("Provide a filter name/ID, or use --default", file=sys.stderr)
        sys.exit(1)

    query = """
    query($mode: FilterMode!) {
      findSavedFilters(mode: $mode) {
        id mode name
        find_filter { q page per_page sort direction }
        object_filter
      }
    }
    """
    data = gql(url, headers, query, {'mode': mode})
    for f in data['findSavedFilters']:
        if str(f['id']) == str(name_or_id) or f['name'].lower() == name_or_id.lower():
            return f, False

    print(f"Filter not found in {mode}: {name_or_id}", file=sys.stderr)
    sys.exit(1)


def cmd_filter_gql(args):
    url, headers = get_connection(args)
    mode = _resolve_filter_mode(args)
    found, is_default = _fetch_saved_filter(url, headers, mode, args)

    find_filter = found.get('find_filter') or {}
    object_filter = found.get('object_filter') or {}

    # Clean find_filter
    find_filter = {k: v for k, v in find_filter.items() if v is not None}

    # Convert UI filter format to GraphQL input format
    object_filter = convert_ui_filter(object_filter)

    # Resolve the GQL query mode (sub-view modes map to their parent mode)
    gql_mode = _subview_parent_mode(mode) if mode in SUBVIEW_MODES else mode
    query_name, filter_arg = MODE_QUERY_MAP[gql_mode]

    if is_default:
        print(f"# Default filter for {mode}")
    else:
        print(f"# Saved filter {mode} id={found['id']}: {json.dumps(found['name'])}")
    print(f"#")

    # Build the GQL query string
    filter_json = json.dumps(find_filter, separators=(',', ':'))
    obj_filter_json = json.dumps(object_filter, indent=2)

    print(f"{{")
    print(f"  {query_name}(")
    print(f"    filter: {filter_json}")
    print(f"    {filter_arg}: {obj_filter_json}")
    print(f"  ) {{")
    print(f"    count")
    print(f"    # Add fields here, e.g.:")
    print(f"    # {_example_fields(gql_mode)}")
    print(f"  }}")
    print(f"}}")


def cmd_filter_url(args):
    url, headers = get_connection(args)
    mode = _resolve_filter_mode(args)
    found, is_default = _fetch_saved_filter(url, headers, mode, args)

    find_filter = found.get('find_filter') or {}
    object_filter = found.get('object_filter') or {}

    # Resolve URL path from mode
    url_mode = _subview_parent_mode(mode) if mode in SUBVIEW_MODES else mode
    path = MODE_URL_PATH.get(url_mode, url_mode.lower())

    # Build the base URL
    gql_url = os.environ.get('STASH_URL', DEFAULT_STASH_ENDPOINT)
    base_url = gql_url.removesuffix('/graphql')

    print(_build_browse_url(base_url, path, find_filter, object_filter))


def _subview_parent_mode(mode):
    """Map a sub-view mode to its parent filter mode."""
    # e.g. PERFORMER_SCENES -> SCENES, STUDIO_IMAGES -> IMAGES
    parts = mode.split('_', 1)
    if len(parts) == 2:
        child = parts[1]
        # Handle multi-word like SUB_GROUPS -> GROUPS, APPEARS_WITH -> PERFORMERS
        child_map = {
            'SUB_GROUPS': 'GROUPS',
            'APPEARS_WITH': 'PERFORMERS',
            'CHILDREN': 'STUDIOS',
            'MARKERS': 'SCENE_MARKERS',
        }
        resolved = child_map.get(child, child)
        if resolved in FILTER_MODES:
            return resolved
    return mode


# Map mode -> URL path segment
MODE_URL_PATH = {
    'SCENES': 'scenes',
    'IMAGES': 'images',
    'PERFORMERS': 'performers',
    'STUDIOS': 'studios',
    'TAGS': 'tags',
    'SCENE_MARKERS': 'markers',
    'GALLERIES': 'galleries',
    'MOVIES': 'groups',
    'GROUPS': 'groups',
}


def _build_browse_url(base_url, path, find_filter, object_filter):
    """Build a Stash browse URL from find_filter and object_filter (UI format)."""
    from urllib.parse import quote, urlencode

    params = []

    # find_filter fields -> query params
    ff = {k: v for k, v in (find_filter or {}).items() if v is not None}
    if 'q' in ff:
        params.append(('q', ff['q']))
    if 'sort' in ff:
        params.append(('sortby', ff['sort']))
    if 'direction' in ff:
        params.append(('sortdir', ff['direction'].lower()))
    if 'per_page' in ff:
        params.append(('perPage', ff['per_page']))
    if 'page' in ff and ff['page'] != 1:
        params.append(('p', ff['page']))

    # object_filter fields -> c= params (one per criterion, in UI format)
    for field_name, criterion in (object_filter or {}).items():
        if not isinstance(criterion, dict):
            c_obj = {"type": field_name, "modifier": "EQUALS", "value": str(criterion).lower()}
        else:
            c_obj = {"type": field_name}
            c_obj.update(criterion)
        params.append(('c', json.dumps(c_obj, separators=(',', ':'))))

    url = f"{base_url}/{path}"
    if params:
        url += '?' + urlencode(params)
    return url


# Map mode → (queryName, filterArgName)
MODE_QUERY_MAP = {
    'SCENES':        ('findScenes',       'scene_filter'),
    'IMAGES':        ('findImages',       'image_filter'),
    'PERFORMERS':    ('findPerformers',   'performer_filter'),
    'STUDIOS':       ('findStudios',      'studio_filter'),
    'TAGS':          ('findTags',         'tag_filter'),
    'SCENE_MARKERS': ('findSceneMarkers', 'scene_marker_filter'),
    'GALLERIES':     ('findGalleries',    'gallery_filter'),
    'MOVIES':        ('findGroups',       'group_filter'),
    'GROUPS':        ('findGroups',       'group_filter'),
}


def _example_fields(mode):
    """Return example field selection for a mode."""
    examples = {
        'SCENES':        'scenes { id title rating100 date studio { name } performers { name } }',
        'IMAGES':        'images { id title tags { name } }',
        'PERFORMERS':    'performers { id name gender favorite }',
        'STUDIOS':       'studios { id name }',
        'TAGS':          'tags { id name }',
        'SCENE_MARKERS': 'scene_markers { id seconds scene { id title } primary_tag { name } }',
        'GALLERIES':     'galleries { id title }',
    }
    return examples.get(mode, '...')


from stash_vroom.util import convert_ui_filter  # noqa: F401 - re-exported for back-compat


# ---------------------------------------------------------------------------
# Command: schema intro
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# Command: schema types
# ---------------------------------------------------------------------------

def cmd_schema_types(args):
    url, headers = get_connection(args)
    data = gql(url, headers, INTROSPECT_TYPES_LIST)
    types = data['__schema']['types']

    # Skip introspection types
    types = [t for t in types if not t['name'].startswith('__')]
    types.sort(key=lambda t: (t['kind'], t['name']))

    rows = []
    for t in types:
        desc = None
        if t.get('description'):
            desc = t['description'].split('\n')[0].split('.')[0].strip()
            if len(desc) > 60:
                desc = desc[:57] + '...'
        rows.append([t['kind'], t['name'], desc])
    print(format_columns(rows))


# ---------------------------------------------------------------------------
# Command: schema type <name>
# ---------------------------------------------------------------------------

def cmd_schema_type(args):
    names = args.names
    is_multi = getattr(args, 'multi', False)

    if len(names) > 1 and not is_multi:
        print("INFO: Multiple types passed; enabling --multi mode", file=sys.stderr)
        is_multi = True

    url, headers = get_connection(args)

    for name in names:
        _print_type(url, headers, name, is_multi)


def _print_type(url, headers, name, is_multi):
    data = gql(url, headers, INTROSPECT_TYPE_DETAIL, {'name': name})
    t = data['__type']

    if not t:
        print(f"Type not found: {name}", file=sys.stderr)
        sys.exit(1)

    if is_multi:
        print(t['name'])
        print('-' * len(t['name']))

    if t.get('fields'):
        rows = []
        for f in t['fields']:
            type_str = render_type_ref(f['type'])
            fname = f['name']
            if f.get('args'):
                arg_parts = []
                for a in f['args']:
                    a_str = f"{a['name']}: {render_type_ref(a['type'])}"
                    if a.get('defaultValue'):
                        a_str += f" = {a['defaultValue']}"
                    arg_parts.append(a_str)
                fname = f"{fname}({', '.join(arg_parts)})"
            rows.append([fname, type_str, f.get('description')])
        print(format_columns(rows))

    if t.get('inputFields'):
        rows = []
        for f in t['inputFields']:
            type_str = render_type_ref(f['type'])
            if f.get('defaultValue'):
                type_str += f" = {f['defaultValue']}"
            desc = f.get('description')
            rows.append([f['name'], type_str, desc])
        print(format_columns(rows))

    if t.get('enumValues'):
        rows = []
        for v in t['enumValues']:
            rows.append([v['name'], v.get('description')])
        print(format_columns(rows))

    if is_multi:
        print()


# ---------------------------------------------------------------------------
# Command: schema queries / schema mutations
# ---------------------------------------------------------------------------

def _print_root_type_fields(args, kind_label):
    url, headers = get_connection(args)
    root_data = gql(url, headers, INTROSPECT_ROOT)

    key = 'queryType' if kind_label == 'Queries' else 'mutationType'
    root_type = root_data['__schema'].get(key)
    if not root_type or not root_type.get('name'):
        print(f"No {kind_label.lower()} type found")
        return

    data = gql(url, headers, INTROSPECT_TYPE_DETAIL, {'name': root_type['name']})
    t = data['__type']

    for f in sorted(t['fields'], key=lambda x: x['name']):
        ret_type = render_type_ref(f['type'])
        if f.get('args'):
            arg_strs = [f"{a['name']}: {render_type_ref(a['type'])}" for a in f['args']]
            print(f"{f['name']}({', '.join(arg_strs)}): {ret_type}")
        else:
            print(f"{f['name']}: {ret_type}")


def cmd_schema_queries(args):
    _print_root_type_fields(args, 'Queries')


def cmd_schema_mutations(args):
    _print_root_type_fields(args, 'Mutations')


# ---------------------------------------------------------------------------
# Command: schema search
# ---------------------------------------------------------------------------

def cmd_schema_search(args):
    url, headers = get_connection(args)
    term = args.term.lower()

    # Single round trip: fetch all types with fields
    data = gql(url, headers, INTROSPECT_FULL)
    all_types = [t for t in data['__schema']['types'] if not t['name'].startswith('__')]

    # Search type names
    type_matches = [t for t in all_types if term in t['name'].lower()
                    or (t.get('description') and term in t['description'].lower())]

    if type_matches:
        print(f"Types matching '{args.term}':")
        for t in sorted(type_matches, key=lambda x: x['name']):
            desc = ''
            if t.get('description'):
                first = t['description'].split('\n')[0].split('.')[0].strip()
                if len(first) > 60:
                    first = first[:57] + '...'
                desc = f'  {first}'
            print(f"  {t['kind']:<14} {t['name']}{desc}")

    # Search field names
    field_matches = []
    for t in all_types:
        fields = t.get('fields') or t.get('inputFields') or []
        for f in fields:
            if term in f['name'].lower() or (f.get('description') and term in f['description'].lower()):
                field_matches.append((t['name'], f['name'], render_type_ref(f['type'])))

    if field_matches:
        if type_matches:
            print()
        print(f"Fields matching '{args.term}':")
        for type_name, field_name, field_type in sorted(field_matches):
            print(f"  {type_name}.{field_name}: {field_type}")

    # Search enum values
    enum_matches = []
    for t in all_types:
        if t.get('enumValues'):
            for v in t['enumValues']:
                if term in v['name'].lower():
                    enum_matches.append((t['name'], v['name']))

    if enum_matches:
        if type_matches or field_matches:
            print()
        print(f"Enum values matching '{args.term}':")
        for type_name, value_name in sorted(enum_matches):
            print(f"  {type_name}.{value_name}")

    if not type_matches and not field_matches and not enum_matches:
        print(f"No matches for '{args.term}'")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        prog='vroom',
        description=__doc__, # This file's docstring
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_read_doc('help.md'),
    )
    #parser._optionals.title = 'Options'
    parser._optionals.title = 'Universal Options'
    parser._optionals.title += ' (rarely needed)'

    parser.add_argument('--url', help=f'Stash GraphQL endpoint; default: {DEFAULT_STASH_ENDPOINT}')

    sub = parser.add_subparsers(dest='command')

    # Remove the auto-generated subcommand group from --help output.
    # The help.md epilog has a better-formatted command list.
    parser._subparsers._group_actions.clear()

    sub.add_parser('version')
    sub.add_parser('config')
    sub.add_parser('stats')

    sub.add_parser('logs',
        description='Greppable list of recent log entries (~30 cached by the server).')

    p_intro = sub.add_parser('intro',
        description='Read introductory guides on a topic.')
    p_intro.add_argument('topic', nargs='?', default=None, help='Topic: queries, discovery, filters, mutations, ui-urls, ui-settings')

    p_query = sub.add_parser('gql',
        description='Execute an arbitrary GraphQL query and print the result as JSON.',
        epilog="Reads from stdin if no query or -f given. Use -f - for explicit stdin.")
    p_query.add_argument('query', nargs='?', help='GraphQL query string')
    p_query.add_argument('-f', '--file', help='Read query from file (use - for stdin)')
    p_query.add_argument('-v', '--variables', help='JSON string of query variables')

    sub.add_parser('filters',
        description='Greppable list of all saved filters across all modes.')

    p_filter = sub.add_parser('filter',
        description='Show a saved filter as GQL query syntax or as a web UI URL.')
    filter_sub = p_filter.add_subparsers(dest='filter_command')

    for subcmd, desc in [('gql', 'Show filter as GQL query syntax'), ('url', 'Show filter as a web UI URL')]:
        p = filter_sub.add_parser(subcmd, description=desc)
        p.add_argument('mode', help='Filter mode: ' + ', '.join(FILTER_MODES))
        p.add_argument('name', nargs='?', default=None, help='Filter name or ID')
        p.add_argument('--default', action='store_true', help='Show the default filter for this mode')

    p_schema = sub.add_parser('schema',
        description='Discover types, fields, queries, and mutations in the Stash GraphQL API.')
    schema_sub = p_schema.add_subparsers(dest='schema_command')

    schema_sub.add_parser('types',
        help='Greppable list of all types (pipe to grep to search)')

    p_type = schema_sub.add_parser('type',
        help='Show all fields for a named type')
    p_type.add_argument('names', nargs='+', help='Type name(s) (e.g. Scene, SceneFilterType, CriterionModifier)')
    p_type.add_argument('--multi', action='store_true', help='Prefix with type name, suffix with blank line')

    schema_sub.add_parser('queries',
        help='List all query operations with argument signatures')

    schema_sub.add_parser('mutations',
        help='List all mutation operations with signatures')

    p_search = schema_sub.add_parser('search',
        help='Search type names, field names, and enum values')
    p_search.add_argument('term', help='Search term (case-insensitive)')

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    # Let piping to head/grep etc. exit cleanly instead of BrokenPipeError.
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    dispatch = {
        'version': cmd_version,
        'config': cmd_config,
        'stats': cmd_stats,
        'gql': cmd_gql,
        'filters': cmd_filters,
        'intro': cmd_intro,
        'logs': cmd_logs,
    }

    if args.command in dispatch:
        try:
            dispatch[args.command](args)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        return

    if args.command == 'filter':
        filter_dispatch = {
            'gql': cmd_filter_gql,
            'url': cmd_filter_url,
        }
        filter_cmd = getattr(args, 'filter_command', None)
        if not filter_cmd:
            parser.parse_args(['filter', '--help'])
            return
        if filter_cmd in filter_dispatch:
            try:
                filter_dispatch[filter_cmd](args)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
            return

    if args.command == 'schema':
        schema_dispatch = {
            'types': cmd_schema_types,
            'type': cmd_schema_type,
            'queries': cmd_schema_queries,
            'mutations': cmd_schema_mutations,
            'search': cmd_schema_search,
        }
        schema_cmd = getattr(args, 'schema_command', None)
        if not schema_cmd:
            parser.parse_args(['schema', '--help'])
            return
        if schema_cmd in schema_dispatch:
            try:
                schema_dispatch[schema_cmd](args)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
            return

    parser.print_help()

if __name__ == '__main__':
    main()
